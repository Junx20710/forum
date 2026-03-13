from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
import pymysql
import bcrypt  # 引入加盐哈希库
import jwt
from datetime import datetime, timedelta, timezone  # 现代时间处理
import re
from contextlib import asynccontextmanager
from config.env_config import Config

# ==================== 正则规则  ====================
# 密码规则：8-16位，必须包含大小写字母、数字和特殊字符
PWD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$"

# 用户名规则：非空，允许字母、数字和下划线，长度3-20
USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,20}$"

# 邮箱标准规则
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# ==================== 通用函数  ====================
def get_current_user(authorization: str = Header(None)):
    """鉴权依赖：从请求头中提取并验证JWT Token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: 未提供有效的认证令牌")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Unauthorized: 认证令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Unauthorized: 认证令牌无效")

# ==================== 现代 Lifespan ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时建表，关闭时清理资源"""
    # 启动阶段：建表
    conn = pymysql.connect(**Config.DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255),
            email VARCHAR(100) UNIQUE
        )
    ''')

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
    
    yield  # 这里是应用运行的时间段

    # 关闭阶段：可以在这里添加资源清理逻辑（如连接池关闭等）

app = FastAPI(lifespan=lifespan)

# ==================== 核心工具函数 ====================
def get_db():
    return pymysql.connect(**Config.DB_CONFIG)

def hash_password(password: str) -> str:
    """使用 bcrypt 进行加盐哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()  # 存储为字符串

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ==================== 接口实现 ====================

class RegisterReq(BaseModel):
    username: str
    password: str
    email: str

@app.post("/api/v2/user/register")
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

class LoginReq(BaseModel):
    username: str
    password: str

@app.post("/api/v2/user/login")
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
        payload = {
            'user_id': user[0],
            'exp': datetime.now(timezone.utc) + timedelta(hours=2)
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        return {"code": 200, "data": {"token": token}}
    return {"code": 401, "msg": "Invalid credentials"}

class PostCreateReq(BaseModel):
    title: str
    content: str

@app.post("/api/v2/posts/create")
def create_post(req: PostCreateReq, user_id: int = Depends(get_current_user)):
    """
    发帖接口：必须通过Depends(get_current_user)来确保只有认证用户才能访问，并且可以直接获取到user_id
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, req.title, req.content, now)
        )
        return {"code": 200, "msg": "发布成功"}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)