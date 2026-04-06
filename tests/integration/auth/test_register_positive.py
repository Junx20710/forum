import pytest
import requests
import allure
from app.core.config import Config

@allure.epic("论坛系统测试")
@allure.feature("用户认证模块")
class TestUserRegisterPositive:

    @allure.story("正向链路：注册、登录和Token提取")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_auth_flow(self, user_factory, setup_teardown_user):
        """
        验证正常用户的注册、登录和Token提取流程
        """
        # 1. 直接从工厂拿“新鲜”且唯一的账号数据
        valid_user = user_factory()
        username = valid_user["username"]

        # 2. 注册并加入清理队列
        with allure.step("步骤1：发送合法注册请求"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=valid_user, timeout=5)
            assert resp.json().get("code") == 200
            # 只要注册成功，立刻塞进清理名单
            setup_teardown_user.append(username)

        # 3. 登录并提取token
        with allure.step("步骤2：发送合法登录请求"):
            login_payload = {"username": username, "password": valid_user["password"]}
            resp_login = requests.post(f"{Config.BASE_URL}/api/v2/user/login", json=login_payload, timeout=5)
            
            res_data = resp_login.json()
            assert res_data.get("code") == 200
            
            token = res_data["data"]["token"]
            assert token.startswith("eyJ") and len(token.split('.')) == 3 # JWT 格式校验
            allure.attach(token, "提取的JWT Token", allure.attachment_type.TEXT)