import pytest
import requests
import allure
from config.env_config import Config

@allure.feature("发帖业务模块")
class TestPostDynamic:

    @allure.story("动态链路：从注册到发帖的全生命周期")
    def test_create_dynamic_post(self, user_factory, setup_teardown_user):
        # 准备数据并注册
        user = user_factory()
        requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=user, timeout=5)
        setup_teardown_user.append(user["username"])


        # 登录并拿token
        login_resp = requests.post(f"{Config.BASE_URL}/api/v2/user/login", 
                                   json={"username": user["username"], "password": user["password"]}, 
                                   timeout=5)
        token = login_resp.json()["data"]["token"]

        # 动态发帖
        post_data = {
            "title": f"{user['username'][-4:]}的测试帖子",
            "content": "这是一篇自动生成的测试帖子"
        }
        headers = {"Authorization": f"Bearer {token}"}
        with allure.step("发送发帖请求"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/posts/create", 
                                 json=post_data, headers=headers, timeout=5)

        assert resp.json().get("code") == 200
