from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import pymysql

from app.schemas.post import PostCreateReq
from app.api.deps import get_db, get_current_user

router = APIRouter

@router.post("/create")
def create_post(req: PostCreateReq, user_id: int = Depends(get_current_user)):
    """
    发帖接口：
    1. 通过 Depends(get_current_user) 自动处理 JWT 鉴权
    2. 只有校验通过的请求才会进入此逻辑
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 获取当前 UTC 时间
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        
        # 写入数据库
        cursor.execute(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, req.title, req.content, now)
        )
        return {"code": 200, "msg": "发布成功"}
    finally:
        conn.close()