import pymysql
import jwt
import redis
from fastapi import Header, HTTPException, Depends
from app.core.config import Config

def get_db():
    return pymysql.connect(**Config.DB_CONFIG)

def get_redis():
    return redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)

def get_current_user(authorization: str = Header(None), r:redis.Redis = Depends(get_redis)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    token = authorization.split(" ")[1]

    if r.get(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="您的账号已在其他地方登出，请重新登录")
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")