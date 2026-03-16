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