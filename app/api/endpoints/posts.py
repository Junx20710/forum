from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
import pymysql

from app.schemas.post import PostCreateReq
from app.api.deps import get_db, get_current_user

router = APIRouter()

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
        conn.commit()
        return {"code": 200, "msg": "发布成功", "data": {"post_id": cursor.lastrowid}}
    finally:
        conn.close()

@router.get("/list")
def get_posts(
    limit: int = Query(10, description="每页数量"), 
    offset: int = Query(0, description="偏移量")
):
    """
    获取帖子列表接口：
    1. 增加分页逻辑，防止压测时一次性拉取过多数据导致内存溢出
    2. 采用 JOIN 查询，同时返回发帖人的用户名
    """
    conn = get_db()
    # 💡 使用 DictCursor 可以让返回结果直接变成字典格式，方便前端/测试解析
    cursor = conn.cursor(pymysql.cursors.DictCursor) 
    try:
        sql = """
            SELECT p.id, p.title, p.content, p.created_at, p.likes_count, u.username 
            FROM posts p 
            JOIN users u ON p.user_id = u.id 
            ORDER BY p.created_at DESC 
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (limit, offset))
        posts = cursor.fetchall()
        return {"code": 200, "data": posts}
    finally:
        conn.close()


@router.post("/{post_id}/like")
def like_post(post_id: int, user_id: int = Depends(get_current_user)):
    """
    点赞/取消点赞接口（Toggle）
    先查后改，严格包裹在事务中
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 事务开启
        conn.begin()

        # 检查是否已经点赞
        cursor.execute("SELECT id FROM post_likes WHERE user_id = %s AND post_id = %s", (user_id, post_id)) 
        existing_like = cursor.fetchone()

        if existing_like:
            # 已点赞 -> 执行取消点赞
            like_id = existing_like[0]
            # 新纪录
            cursor.execute("DELETE FROM post_likes WHERE id = %s", (like_id,))
            # 帖子赞数 -1
            cursor.execute("UPDATE posts SET likes_count = likes_count - 1 WHERE id = %s", (post_id,))
            msg = "取消点赞成功"
        else:
            # 未点赞 -> 执行点赞
            cursor.execute("INSERT INTO post_likes (user_id, post_id) VALUES(%s, %s)", (user_id, post_id))
            # 帖子赞数 +1
            cursor.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE id = %s", (post_id,))
            msg = "点赞成功"
        conn.commit()
        return {"code": 200, "msg": msg}
    except Exception as e:
        # 发生任何异常都应该rollback保持likes_count和post_likes的绝对一致性
        conn.rollback()
        return {"code": 500, "msg": f"系统异常：{str(e)}"}
    finally:
        conn.close()