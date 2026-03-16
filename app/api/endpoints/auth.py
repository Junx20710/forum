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