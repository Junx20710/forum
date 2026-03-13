# utils/db_util.py
import pymysql
import allure

class DBUtil:
    def __init__(self, conn):
        # 核心优化：不再自己建立连接，而是复用 fixture 传进来的连接
        self.conn = conn

    def delete_users_bulk(self, usernames: list):
        """
        批量删除用户，效率比循环单次删除高 10 倍以上
        """
        if not usernames:
            return
            
        with allure.step(f"[DB] 批量物理删除测试用户: {usernames}"):
            cursor = self.conn.cursor()
            try:
                # 级联删除逻辑：配合数据库的 ON DELETE CASCADE
                format_strings = ','.join(['%s'] * len(usernames))
                sql = f"DELETE FROM users WHERE username IN ({format_strings})"
                
                # 在 Allure 报告中记录执行的 SQL
                allure.attach(sql, "执行的清理 SQL", allure.attachment_type.TEXT)
                
                cursor.execute(sql, tuple(usernames))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                allure.attach(str(e), "数据库清理异常", allure.attachment_type.TEXT)
                raise e
            finally:
                cursor.close()