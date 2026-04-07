# conftest.py
import pytest
import allure
import uuid
from utils.db_util import DBUtil
import pymysql
from app.core.config import Config
from utils.data_factory import DataFactory
from fastapi.testclient import TestClient
from app.main import app

# 1. 基础连接：Session 级，整个测试周期只连一次
@pytest.fixture(scope="session")
def db_conn():
    with allure.step("🔧 [Setup] 建立全局数据库长连接"):
        conn = pymysql.connect(**Config.DB_CONFIG)
        yield conn
    with allure.step("🧹 [Teardown] 关闭数据库全局连接"):
        conn.close()

# 2. 工具对象：将连接包装成工具类
@pytest.fixture
def db_tool(db_conn):
    return DBUtil(db_conn)

# 3. 造血中心：保持动态性
@pytest.fixture
def user_factory():
    def _make_user():
        data = DataFactory.build_user()
        allure.attach(str(data), "工厂生成的动态数据", allure.attachment_type.TEXT)
        return data
    return _make_user

# 4. 核心清理逻辑：生产后清除
@pytest.fixture
def setup_teardown_user(db_tool):
    """
    只需将生成的 username append 到这个 list 里，
    用例结束后会自动触发 db_tool 进行级联清理。
    """
    users_to_clean = []

    yield users_to_clean 

    # 这里的代码在测试用例结束后执行
    if users_to_clean:
        db_tool.delete_users_bulk(users_to_clean)
# 5. 全局测试客户端：取代requests：实现同进程级别的集成测试
@pytest.fixture(scope="session")
def api_client():
    with allure.step("[SetUP] 初始化FastAPI 测试客户端"):
        with TestClient(app) as client:
            yield client
