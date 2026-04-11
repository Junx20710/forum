import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    # ============================================
    # 应用配置
    # ============================================
    FORUM_HOST = os.getenv("FORUM_HOST", "127.0.0.1")
    FORUM_PORT = int(os.getenv("FORUM_PORT", 8000))
    BASE_URL = os.getenv("FORUM_BASE_URL", "http://127.0.0.1:8000")

    # ============================================
    # 安全配置
    # ============================================
    SECRET_KEY = os.getenv("FORUM_SECRET_KEY", "your-super-safe-and-long-secret-key-here")

    # ============================================
    # 数据库配置
    # ============================================
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", 3309)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "forum_db"),
        "autocommit": os.getenv("DB_AUTOCOMMIT", "True").lower() == "true"
    }

    # ============================================
    # Redis 配置
    # ============================================
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

    # ============================================
    # 性能测试配置
    # ============================================
    PREF_USER_COUNT = int(os.getenv("FORUM_PERF_USER_COUNT", 1200))