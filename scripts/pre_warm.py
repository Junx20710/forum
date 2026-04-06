import csv
import os
import pymysql

from utils.data_factory import DataFactory
from app.core.security import hash_password
from app.core.config import Config

def warm_up_users(count=Config.PREF_USER_COUNT, output_file="test_users.csv"):
    conn = pymysql.connect(**Config.DB_CONFIG)
    cursor = conn.cursor
    user_to_export = []

    for _ in range(count):
        user = DataFactory.build_user()

        hashed_pwd = hash_password(user["password"])
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (user["username"], hashed_pwd, user["email"])
        )
        user_to_export.append(user["username", user["password"]])

    conn.commit()
    conn.close()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password"])
        writer.writerows(user_to_export)


if __name__ == "__main__":
    warm_up_users()
