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
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN likes_count INT DEFAULT 0")
    except pymysql.err.OperationalError as e:
        if e.args[0] != 1060:  # 1060 是列已存在的错误代码
            pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            post_id INT,
            UNIQUE KEY unique_like (user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
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