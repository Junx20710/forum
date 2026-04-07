from fastapi import APIRouter, HTTPException, Response, Depends, Header
import re
import redis
import jwt
from datetime import datetime, timezone
import pymysql
from app.schemas.user import RegisterReq, LoginReq
from app.core.security import (
    hash_password, verify_password, create_access_token,
    PWD_PATTERN, USERNAME_PATTERN, EMAIL_PATTERN
)
from app.core.config import Config
from app.api.deps import get_db, get_redis

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
        conn.commit()
        return {"code": 200, "msg": "Register Success"}
    except pymysql.err.IntegrityError:
        return {"code": 400, "msg": "Username or Email already exists"}
    finally:
        conn.close()

@router.post("/login")
def login(req: LoginReq, response: Response):
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
    response.status_code = 401
    return {"code": 401, "msg": "Invalid credentials"}

@router.post("/logout")
def logout(authorization: str = Header(None), r:redis.Redis = Depends(get_redis)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"code": 401, "msg": "无有效token"}
    token = authorization.split(" ")[1].strip()

    try:
        # 解析token拿到后的到期时间
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        exp = payload.get('exp')
        now = datetime.now(timezone.utc).timestamp()

        # 计算剩余寿命
        ttl = int(exp - now)
        if ttl > 0:
            # 将token压入Reids黑名单，并设置TTL
            r.setex(f"blacklist:{token}", ttl ,"1")
    except Exception:
        return {"code": 401, "msg": "无效的Token或已过期"}

    return {"code": 200, "msg": "注销成功"}

