import csv
import os
import time
import pymysql

from utils.data_factory import DataFactory
from app.core.security import hash_password
from app.core.config import Config

def warm_up_users(output_file="test_users.csv"):
    start_time = time.time
    count = Config.PREF_USER_COUNT

    conn = pymysql.connect(**Config.DB_CONFIG)
    cursor = conn.cursor()

    user_to_export = []
    db_insert_data = []

    # 仅执行一次密码 hash
    common_pwd = "Password123!"
    hash_pwd = hash_password(common_pwd)

    for _ in range(count):
        user = DataFactory.build_user()
        username = user["username"]
        email = user["email"]

        # 参数打包成元组，存入列表
        db_insert_data.append((username, hash_pwd, email))
        user_to_export.append([username, common_pwd])
    
    # 批量插入 (Bulk Insert) 解决 I/O 阻塞
    sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
    cursor.executemany(sql, db_insert_data)

    conn.commit()
    conn.close()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password"])
        writer.writerows(user_to_export)


if __name__ == "__main__":
    warm_up_users()
