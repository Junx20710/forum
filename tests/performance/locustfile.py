import os
import csv
import uuid
import random
import pymysql
import time
import allure_commons
from allure_commons.model2 import TestResult, Status, Label
from allure_commons.types import LabelType
from allure_commons.logger import AllureFileLogger
from locust import FastHttpUser, task, between, events
from locust.exception import StopUser

from app.core.config import Config
from utils.db_util import DBUtil
from utils.data_factory import DataFactory

results_dir = "allure-results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

allure_commons.plugin_manager.register(AllureFileLogger(results_dir))
# ================= 1. Allure 报告桥接监听器 =================
@events.request.add_listener
def on_request_to_allure(request_type, name, response_time, response_length, exception, context, **kwargs):
    """将 Locust 的每一次请求实时同步到 Allure 结果集中"""
    status = Status.PASSED if exception is None else Status.FAILED
    
    result = TestResult(
        uuid=str(uuid.uuid4()),
        name=f"[{request_type}] {name}",
        status=status,
        start=int(time.time() * 1000) - response_time,
        stop=int(time.time() * 1000)
    )
    # 分类标签，方便在 Allure 报告中筛选
    result.labels.append(Label(name=LabelType.FEATURE, value="压力测试"))
    result.labels.append(Label(name=LabelType.STORY, value=name))
    
    # 写入 allure-results 目录（与 pytest 共享）
    allure_commons.plugin_manager.hook.report_result(result=result)


# ================= 2. 加载预热好的“弹药库” =================
warm_users = []
try:
    with open("test_users.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            warm_users.append(row)
    print(f"✅ [Locust] 成功加载预热数据池：{len(warm_users)} 个账号")
except FileNotFoundError:
    print("❌ [Locust] 找不到 test_users.csv，请先运行 scripts/pre_warm.py！")


# ================= 3. 自动扫尾 (Teardown) =================
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """当压测停止时，自动调用 DBUtil 清理预热产生的僵尸账号"""
    print("\n🧹 [Teardown] 压测结束，正在清理测试数据...")
    usernames = []
    try:
        # 重新读取 CSV 获取所有需要清理的用户名
        with open("test_users.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            usernames = [row["username"] for row in reader]

        if usernames:
            conn = pymysql.connect(**Config.DB_CONFIG)
            db_tool = DBUtil(conn)
            # 💡 复用 db_util 的批量物理删除逻辑
            db_tool.delete_users_bulk(usernames)
            conn.close()
            print(f"✅ [Teardown] 已成功物理删除 {len(usernames)} 个账号及其关联帖子")
    except Exception as e:
        print(f"❌ [Teardown] 清理失败: {str(e)}")


# ================= 4. 用户画像 A：首日注册登录洪峰 (Rush) =================
class DayOneRushUser(FastHttpUser):
    """模拟新用户涌入，主要测试注册和登录接口的 CPU 消耗（Bcrypt 哈希）"""
    weight = 1  # 权重 1
    wait_time = between(0.1, 0.5)  # 连点器级别的频率

    @task
    def rush_register_login(self):
        # 直接复用 DataFactory 造数，确保不重复
        user = DataFactory.build_user()
        
        # 注册动作
        with self.client.post("/api/v2/user/register", json=user, catch_response=True, name="[Rush] 注册新账号") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"注册失败: {resp.text}")

        # 登录动作
        self.client.post("/api/v2/user/login", json={
            "username": user["username"],
            "password": user["password"]
        }, name="[Rush] 立即登录")


# ================= 5. 用户画像 B：日常权重行为 (Daily) =================
class DailyActiveUser(FastHttpUser):
    """模拟正常老用户，直接从预热池拿账号，重点测发帖写入性能"""
    weight = 5  # 权重 5（老用户是主力）
    # 缩短时间间隔，增加请求频率，触发redis限流逻辑，验证预热数据的有效性
    wait_time = between(1, 3)

    def on_start(self):
        """出生逻辑：从池子里 pop 一个账号并登录"""

        self.headers = {}
        
        if not warm_users:
            print("⚠️ [Daily] 预热账号池已空，无法模拟登录！")
            raise StopUser()

        # 💡 pop() 保证并发下账号不冲突
        self.user_data = warm_users.pop()
        
        
        resp = self.client.post("/api/v2/user/login", json=self.user_data, name="[Daily] 预热账号登录")
        if resp.status_code == 200 and resp.json().get("code") == 200:
            token = resp.json().get("data", {}).get("token")
            if token:
                self.headers = {"Authorization": f"Bearer {token}"}
    def on_stop(self):
        if self.headers:
            self.client.post("/api/v2/user/logout", headers=self.headers, name="[Daily] 预热账号登出")

    @task(10)
    def view_posts(self):
        """模拟刷帖（高频）"""
        self.client.get("/api/v2/posts/list", name="[Daily] 查看帖子列表")

    @task(5) # 提高发帖频率，逼出限流
    def create_post(self):
        if not self.headers: return
        
        payload = {
            "title": f"压测发帖_{uuid.uuid4().hex[:6]}",
            "content": "性能测试内容填充..."
        }
        self.client.post("/api/v2/posts/create", json=payload, headers=self.headers, name="[Daily] 发布新帖子")

        with self.client.post("/api/v2/posts/create", json=payload, headers=self.headers, name="[Daily] 发布新帖子", catch_response=True) as resp:
            # 200 是真正的业务成功
            if resp.status_code == 200:
                resp.success()
            # 💡 429 是 Redis 成功拦截了！在压测中这属于防刷策略生效，我们把它标记为绿色（成功），并单独记录
            elif resp.status_code == 429:
                resp.success() 
                # 你会在日志里看到这个，但 Allure 报告里不会报错
            else:
                resp.failure(f"崩溃异常! 状态码: {resp.status_code}, 内容: {resp.text}")