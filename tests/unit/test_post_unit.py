import pytest
import allure
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user, get_redis

client = TestClient(app)

def override_get_current_user():
    return 999

@allure.feature("用户模块")
@allure.story("用户发帖")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_post_mock_auth_and_db(mocker):
    '''
    单元测试：跳过JWT和db，单纯测试发帖业务
    '''
    try:
        with allure.step("1. 覆盖依赖"):
            app.dependency_overrides[get_current_user] = override_get_current_user

            # mock掉数据库依赖
            mock_conn = mocker.Mock()
            mock_cursor = mocker.Mock()
            mock_cursor.lastrowid = 1
            mocker.patch("app.api.endpoints.posts.get_db", return_value=mock_conn)
            mock_conn.cursor.return_value = mock_cursor
            
            # mock掉Redis, 假装用户是第一次发帖，骗过限流
            mock_redis = mocker.Mock()
            mock_redis.incr.return_value = 1
            app.dependency_overrides[get_redis] = lambda: mock_redis
            

        with allure.step("2. 发送请求"):
            payload = {
                "title": "Mock test",
                "content": "Mock content"
            }
            resp = client.post("/api/v2/posts/create", json=payload)


        with allure.step("3. 状态验证"):
            assert resp.json().get("code") == 200

        with allure.step("4. 行为验证"):
            called_sql, called_args = mock_cursor.execute.call_args[0]
            assert called_args[0] == 999  # user_id 
            assert called_args[1] == "Mock test"

    finally:
        app.dependency_overrides.clear()