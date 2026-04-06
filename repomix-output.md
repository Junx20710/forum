This file is a merged representation of the entire codebase, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
.github/workflows/api_test_ci.yml
.gitignore
app/__init__.py
app/api/__init__.py
app/api/deps.py
app/api/endpoints/__init__.py
app/api/endpoints/auth.py
app/api/endpoints/posts.py
app/core/__init__.py
app/core/config.py
app/core/security.py
app/main.py
app/schemas/__init__.py
app/schemas/post.py
app/schemas/user.py
conftest.py
docker-compose.yml
pytest.ini
requirements.txt
tests/auth/test_register_negative.py
tests/auth/test_register_positive.py
tests/posts/test_post_api.py
utils/__init__.py
utils/db_util.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="app/__init__.py">

</file>

<file path="app/api/__init__.py">

</file>

<file path="app/api/endpoints/__init__.py">

</file>

<file path="app/core/__init__.py">

</file>

<file path="app/core/config.py">
import os

class Config:
    BASE_URL = "http://127.0.0.1:8000"

    SECRET_KEY = os.getenv("FORUM_SECRET_KEY", "your-super-safe-and-long-secret-key-here")

    # Docker MySQL 配置
    DB_CONFIG = {
        "host": "127.0.0.1",
        "port": 3309,
        "user": "root",
        "password": "root",
        "database": "forum_db",
        "autocommit": True
    }
</file>

<file path="app/core/security.py">
import bcrypt
import jwt
import re
from datetime import datetime, timedelta, timezone
from app.core.config import Config

# ==================== 正则规则  ====================
# 密码规则：8-16位，必须包含大小写字母、数字和特殊字符
PWD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$"

# 用户名规则：非空，允许字母、数字和下划线，长度3-20
USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,20}$"

# 邮箱标准规则
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=2)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
</file>

<file path="app/schemas/__init__.py">

</file>

<file path="app/schemas/post.py">
from pydantic import BaseModel, Field, ConfigDict

class PostCreateReq(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
</file>

<file path="app/schemas/user.py">
from pydantic import BaseModel

class RegisterReq(BaseModel):
    username: str
    password: str
    email: str

class LoginReq(BaseModel):
    username: str
    password: str
</file>

<file path="docker-compose.yml">
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: forum_mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: forum_db
    ports:
      # 宿主机端口:容器端口
      - "3309:3306"
    command: --default-authentication-plugin=mysql_native_password
    volumes:
      # 将容器内的数据映射到当前目录下的 mysql_data 文件夹
      - ./mysql_data:/var/lib/mysql
</file>

<file path="pytest.ini">
[pytest]
# 1. 配置默认执行参数
# -v: 详细模式  -s: 打印代码中的 print 信息
# --alluredir: 指定 allure 原始数据生成路径
# --clean-alluredir: 每次运行前清空旧的报告数据
addopts = -vs --alluredir=./reports --clean-alluredir

# 2. 配置测试搜索路径
# 告诉 pytest 只去 tests 目录下找用例，提升启动速度
testpaths = tests

# 3. 配置测试文件、类、函数的命名规则
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 4. 解决控制台 Unicode 乱码问题 (核心！)
# 设置为 True 后，DDT 数据池里的中文描述将不再显示为 \uXXXX，而是直接显示中文
disable_test_id_escaping_and_forfeit_all_rights_to_complain = True

# 5. 配置日志格式 (可选，方便调试)
log_cli = True
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)
log_cli_date_format = %Y-%m-%d %H:%M:%S
</file>

<file path="utils/__init__.py">

</file>

<file path="utils/db_util.py">
# utils/db_util.py
import pymysql
import allure

class DBUtil:
    def __init__(self, conn):
        # 核心优化：不再自己建立连接，而是复用 fixture 传进来的连接
        self.conn = conn

    def delete_users_bulk(self, usernames: list):
        """
        批量删除用户，效率比循环单次删除高 10 倍以上
        """
        if not usernames:
            return
            
        with allure.step(f"[DB] 批量物理删除测试用户: {usernames}"):
            cursor = self.conn.cursor()
            try:
                # 级联删除逻辑：配合数据库的 ON DELETE CASCADE
                format_strings = ','.join(['%s'] * len(usernames))
                sql = f"DELETE FROM users WHERE username IN ({format_strings})"
                
                # 在 Allure 报告中记录执行的 SQL
                allure.attach(sql, "执行的清理 SQL", allure.attachment_type.TEXT)
                
                cursor.execute(sql, tuple(usernames))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                allure.attach(str(e), "数据库清理异常", allure.attachment_type.TEXT)
                raise e
            finally:
                cursor.close()
</file>

<file path=".gitignore">
__pycache__/
*.pyc
.env
allure-results/
allure-report/
.pytest_cache/
venv/
.vscode/
mysql_data/
reports/
</file>

<file path="app/api/deps.py">
import pymysql
import jwt
from fastapi import Header, HTTPException
from app.core.config import Config

def get_db():
    return pymysql.connect(**Config.DB_CONFIG)

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")
</file>

<file path="app/api/endpoints/auth.py">
from fastapi import APIRouter, HTTPException
import re
import pymysql
from app.schemas.user import RegisterReq, LoginReq
from app.core.security import (
    hash_password, verify_password, create_access_token,
    PWD_PATTERN, USERNAME_PATTERN, EMAIL_PATTERN
)
from app.api.deps import get_db

router = APIRouter()

@router.post("/register")
def register(req: RegisterReq):
    # 用户名非空与格式校验
    if not req.username or not re.match(USERNAME_PATTERN, req.username):
        return {"code": 400, "msg": "非法用户名：格式错误或长度不符"}
    
    # 密码复杂度校验
    if not re.match(PWD_PATTERN, req.password):
        return {"code": 400, "msg": "密码必须为8-16位且包含大小写字母、数字及特殊字符"}
    
    # 邮箱格式校验
    if not req.email or not re.match(EMAIL_PATTERN, req.email):
        return {"code": 400, "msg": "非法邮箱：格式错误"}
    
    hashed_pwd = hash_password(req.password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (req.username, hashed_pwd, req.email)
        )
        return {"code": 200, "msg": "Register Success"}
    except pymysql.err.IntegrityError:
        return {"code": 400, "msg": "Username or Email already exists"}
    finally:
        conn.close()

@router.post("/login")
def login(req: LoginReq):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password FROM users WHERE username=%s",
        (req.username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(req.password, user[1]):
        # 签发 JWT Token
        token = create_access_token(user_id=user[0])
        return {"code": 200, "data": {"token": token}}
    return {"code": 401, "msg": "Invalid credentials"}
</file>

<file path="app/api/endpoints/posts.py">
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import pymysql

from app.schemas.post import PostCreateReq
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.post("/create")
def create_post(req: PostCreateReq, user_id: int = Depends(get_current_user)):
    """
    发帖接口：
    1. 通过 Depends(get_current_user) 自动处理 JWT 鉴权
    2. 只有校验通过的请求才会进入此逻辑
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 获取当前 UTC 时间
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        # 写入数据库
        cursor.execute(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, req.title, req.content, now)
        )
        return {"code": 200, "msg": "发布成功"}
    finally:
        conn.close()
</file>

<file path="conftest.py">
# conftest.py
import pytest
import allure
import uuid
from utils.db_util import DBUtil
import pymysql
from app.core.config import Config

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
        unique_id = uuid.uuid4().hex[:6]
        username = f"user_{unique_id}"
        data = {
            "username": username,
            "password": "Password123!",
            "email": f"{username}@test.com"
        }
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
</file>

<file path="requirements.txt">
# --- 后端框架 ---
fastapi[all]          # FastAPI 核心框架（包含 pydantic 和 email-validator）
uvicorn[standard]     # 高性能 ASGI 服务器

# --- 数据库驱动 ---
pymysql               # MySQL 数据库连接驱动

# --- 安全与加密 ---
pyjwt                 # JWT Token 签发与解析
passlib[bcrypt]       # 工业级密码哈希处理
cryptography>=3.4.7

# --- 自动化测试 ---
pytest                # 单元与集成测试框架
requests              # 测试脚本发送 API 请求
allure-pytest         # 生成 Allure 专业测试报告

# --- 环境配置 ---
python-dotenv         # 自动从 .env 文件加载环境变量
</file>

<file path="tests/auth/test_register_negative.py">
import uuid
import pytest
import requests
import allure
from app.core.config import Config

# 每一个元组代表：（username, password, email，expected code，description）
REGISTRATION_DDT_POOL = [
    # 3-point BVA n n-1 n+1: password必须在8-16位，且包含大小写字母、数字和特殊字符
    ("invalid_user1_short", "A"*4 + "a1!", "invalid1@example.com", 400, "非法密码：8-1位，边界值校验"),
    ("valid_user1", "A"*5 + "a1!", "valid1@example.com", 200, "合法密码：8位加混合字符"),
    ("valid_user2", "A"*6 + "a1!", "valid2@example.com", 200, "合法密码：8+1位加混合字符"),
    ("valid_user3", "A"*12 + "a1!", "valid3@example.com", 200, "合法密码：16-1位加混合字符"),
    ("valid_user4", "A"*13 + "a1!", "valid4@example.com", 200, "合法密码：16位加混合字符"),
    ("invalid_user2_long", "A"*14 + "a1!", "invalid2@example.com", 400, "非法密码：16+1位，边界值校验"),

    # complexity checks: password必须包含大小写字母、数字和特殊字符
    ("invalid_user3_no_upper", "a"*8 + "1!", "invalid3@example.com", 400, "非法密码：无大写字母"),
    ("invalid_user4_no_lower", "A"*8 + "1!", "invalid4@example.com", 400, "非法密码：无小写字母"),
    ("invalid_user5_no_digit", "A"*8 + "a!", "invalid5@example.com", 400, "非法密码：无数字"),
    ("invalid_user6_no_special", "A"*8 + "a1!", "invalid6@example.com", 400, "非法密码：无特殊字符"),

    # username checks
    ("", "A"*8 + "a1!", "invalid7@example.com", 400, "非法用户名：空用户名"),

    # mail checks
    ("invalid_user8", "A"*8 + "a1!", "", 400, "非法邮箱：空邮箱"),
    ("invalid_user9", "A"*8 + "a1!", "invalid-email-format", 400, "非法邮箱：格式错误"),

]

@allure.epic("论坛系统测试")
@allure.feature("用户认证模块")
@allure.story("异常校验：DDT")
class TestUserRegisterNegative:

    @pytest.mark.parametrize("username, password, email, expected_code, description", REGISTRATION_DDT_POOL)
    def test_register_negative_rules(self, setup_teardown_user, username, password, email, expected_code, description):
        """
        利用参数化技术，批量验证后端拦截逻辑是否生效
        """
        allure.dynamic.title(f"注册异常校验: {description}")

        # 只有用户名不为空时才加 UUID，确保测试场景真实
        unique_name = f"{username}_{str(uuid.uuid4())[:8]}" if username != "" else ""

        payload = {
            "username": unique_name,
            "password": password,
            "email": email
        }

        with allure.step(f"执行异常数据测试：{description}"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=payload, timeout=5)
            res_json = resp.json()

            # 只有误操作注册成功时，才需要加入清理列表
            if res_json.get("code") == 200:
                setup_teardown_user.append(unique_name)

            # 断言：校验 code 和后端返回的 msg
            assert res_json.get("code") == expected_code, \
                f"失败！预期 {expected_code}，但返回 {res_json.get('code')}, 详情：{res_json.get('msg')}"
</file>

<file path="tests/auth/test_register_positive.py">
import pytest
import requests
import allure
from app.core.config import Config

@allure.epic("论坛系统测试")
@allure.feature("用户认证模块")
class TestUserRegisterPositive:

    @allure.story("正向链路：注册、登录和Token提取")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_auth_flow(self, user_factory, setup_teardown_user):
        """
        验证正常用户的注册、登录和Token提取流程
        """
        # 1. 直接从工厂拿“新鲜”且唯一的账号数据
        valid_user = user_factory()
        username = valid_user["username"]

        # 2. 注册并加入清理队列
        with allure.step("步骤1：发送合法注册请求"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=valid_user, timeout=5)
            assert resp.json().get("code") == 200
            # 只要注册成功，立刻塞进清理名单
            setup_teardown_user.append(username)

        # 3. 登录并提取token
        with allure.step("步骤2：发送合法登录请求"):
            login_payload = {"username": username, "password": valid_user["password"]}
            resp_login = requests.post(f"{Config.BASE_URL}/api/v2/user/login", json=login_payload, timeout=5)
            
            res_data = resp_login.json()
            assert res_data.get("code") == 200
            
            token = res_data["data"]["token"]
            assert token.startswith("eyJ") and len(token.split('.')) == 3 # JWT 格式校验
            allure.attach(token, "提取的JWT Token", allure.attachment_type.TEXT)
</file>

<file path="app/main.py">
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import pymysql

# 💡 引入解耦的路由和配置
from app.api.endpoints import auth, posts
from app.core.config import Config

# 1. 💡 找回丢失的自动建表逻辑 (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时建表"""
    conn = pymysql.connect(**Config.DB_CONFIG)
    cursor = conn.cursor()
    
    # 建 users 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255),
            email VARCHAR(100) UNIQUE
        )
    ''')

    # 建 posts 表，包含级联删除
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(100),
            content TEXT,
            created_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.close()
    yield  # 应用运行

# 2. 实例化应用，并绑定 lifespan
app = FastAPI(title="Forum API Pro", lifespan=lifespan)

# 3. 全局异常拦截器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=200, 
        content={"code": 400, "msg": "请求参数校验失败", "detail": exc.errors()}
    )

# 4. 💡 精确挂载路由（解决 404 Not Found 的关键）
# 注意这里的 prefix 必须是 "/api/v2/user"，这样加上 auth.py 里的 "/register" 才是完整路径
app.include_router(auth.router, prefix="/api/v2/user", tags=["用户认证"])
app.include_router(posts.router, prefix="/api/v2/posts", tags=["帖子业务"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
</file>

<file path="tests/posts/test_post_api.py">
import pytest
import requests
import allure
from app.core.config import Config




@allure.feature("发帖业务模块")
class TestPostDynamic:

    # DDT POOL(title, content, token_type, expected_code, description)
    

    @allure.story("动态链路：从注册到发帖的全生命周期")
    def test_create_dynamic_post(self, user_factory, setup_teardown_user):
        # 准备数据并注册
        user = user_factory()
        requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=user, timeout=5)
        setup_teardown_user.append(user["username"])


        # 登录并拿token
        login_resp = requests.post(f"{Config.BASE_URL}/api/v2/user/login", 
                                   json={"username": user["username"], "password": user["password"]}, 
                                   timeout=5)
        token = login_resp.json()["data"]["token"]

        # 动态发帖
        post_data = {
            "title": f"{user['username'][-4:]}的测试帖子",
            "content": "这是一篇自动生成的测试帖子"
        }
        headers = {"Authorization": f"Bearer {token}"}
        with allure.step("发送发帖请求"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/posts/create", 
                                 json=post_data, headers=headers, timeout=5)

        assert resp.json().get("code") == 200

    POST_DDT_POOL = [
        ("A"*101, "正常内容", "valid", 400, "边界值：标题超长"),
        ("正常标题", "正常内容", "invalid", "401", "等价类：伪造的无效token"),
        ("   ", "   ", "valid", 400, "错误推测：标题和内容全为空格"),
    ]


    @allure.story("异常用例测试")
    @pytest.mark.parametrize("title, content, token_type, expected_code, description", POST_DDT_POOL)
    def test_post_negative(self, user_factory, setup_teardown_user, title, content, token_type, expected_code, description):
        """
        利用数据驱动验证发帖接口的边界值与鉴权拦截逻辑
        """
        allure.dynamic.title(f"发帖拦截校验：{description}")
        # 根据用例要求决定是否发真token
        token = "fake_and_invalid_token_string_eyJhb..."
        if token_type == "valid":
            user = user_factory()
            # 注册并加进清理队列
            requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=user, timeout=5)
            setup_teardown_user.append(user["username"])

            # 登录，且成功才会拿真token
            login_resp = requests.post(f"{Config.BASE_URL}/api/v2/user/login",
                                        json={"username": user["username"], "password": user["password"]}, 
                                        timeout=5)
            login_data = login_resp.json()
            if login_resp.status_code == 200 and "data" in login_data:
                token = login_data["data"]["token"]
            else:
                pytest.fail(f"测试前置条件不满足：无法返回有效token，返回： {login_data}")

        # 发送异常请求
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"title": title, "content": content}

        with allure.step(f"发送破坏性请求:{description}"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/posts/create",
                                json=payload, headers=headers,
                                timeout=5)
        

        res_json = resp.json()
        actual_code = res_json.get("code") or resp.status_code
        assert int(actual_code) == int(expected_code), \
            f"拦截失败！返回预期返回码 {expected_code}，实际返回: {actual_code}"
</file>

<file path=".github/workflows/api_test_ci.yml">
name: Forum API Automation CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main ]

permissions:
  contents: write

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: forum_db
        ports:
          - 3309:3306 
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      with:
        fetch-depth: 0 

    - name: 设置 Python 3.9 环境
      uses: actions/setup-python@v5
      with:
        python-version: '3.9'
        cache: 'pip'

    - name: 安装项目依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: 启动后端并运行测试
      env:
        SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
        # 💡 设置 PYTHONPATH 确保机器人能找到 app 包
        PYTHONPATH: .
      run: |
        # 💡 关键改动：路径从 main:app 变为 app.main:app
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 & 
        
        sleep 5

        echo "================ 后端启动日志 ================"
        cat backend.log
        echo "============================================="
        sleep 10
        # 即使测试失败也继续，保证生成报告
        pytest --alluredir=./allure-results || true 

    - name: 渲染 Allure 报告
      uses: simple-elf/allure-report-action@master
      if: always()
      id: allure-report
      with:
        report_dir: allure-results
        gh_pages: gh-pages
        allure_report: allure-report
        allure_history: allure-history
    
    - name: 推送报告到 gh-pages
      uses: peaceiris/actions-gh-pages@v3
      if: always()
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_branch: gh-pages
        publish_dir: allure-history
</file>

</files>
