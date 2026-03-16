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