from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import pymysql

# 💡 引入解耦的路由和配置
from app.api.endpoints import auth, posts

# 2. 实例化应用，并绑定 lifespan
app = FastAPI(title="Forum API Pro")

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