import os

class Config:
    BASE_URL = "http://127.0.0.1:5000"

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