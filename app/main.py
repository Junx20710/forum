# app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.endpoints import auth, posts
from app.core.config import Config
import pymysql

app = FastAPI(title="Forum API Pro")

# 全局异常拦截
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=200, content={"code": 400, "msg": "参数校验失败", "detail": exc.errors()})

# 💡 挂载模块：解耦的核心
app.include_router(auth.router, prefix="/api/v2/user", tags=["用户模块"])
app.include_router(posts.router, prefix="/api/v2/posts", tags=["发帖模块"])
app.include_router(
    posts.router, 
    prefix="/api/v2/posts", # 这里定义了 URL 的前缀
    tags=["发帖模块"]        # 在 Swagger 文档中会显示的分组
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)