import pytest
import allure
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@allure.feature("用户模块")
@allure.story("用户注册")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_success_mock_db(mocker):
    '''
    单元测试： 验证注册逻辑在数据库正常时，能否正确返回200并正确调用了sql
    '''
    with allure.step("1. 准备Mock环境"):
        mock_conn = mocker.Mock()
        mock_cursor = mocker.Mock()

        # 拦截auth.py里的get_d调用，返回mocker
        mocker.patch("app.api.endpoints.auth.get_db", return_value = mock_conn)
        mock_conn.cursor.return_value = mock_cursor

    with allure.step("2. 发起注册请求"):
        payload = {
            "username": "mockuser",
            "password": "Password123!",
            "email": "mock@test.com"
        }
        resp = client.post("/api/v2/user/register", json=payload)

    with allure.step("3. 状态验证"):
        assert resp.status_code == 200
        assert resp.json().get("code") == 200

    with allure.step("4. 行为验证"):
        assert mock_cursor.execute.call_count == 1

        # 获取execute被调用时的参数
        called_sql, called_args = mock_cursor.execute.call_args[0]
        assert "INSERT INTO users" in called_sql
        assert called_args[0] == "mockuser"

        # 检查密码是否被加密（不应该存在明文）
        assert called_args[1] != "Password123!"

        mock_conn.commit.assert_called_once()

