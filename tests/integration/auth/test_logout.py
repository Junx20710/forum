import pytest
import allure

@allure.epic("论坛系统测试")
@allure.feature("用户认证模块")
@allure.story("登出功能正负向测试")
class TestUserLogout:

    @allure.title("正向：合法Token登出后，Token失效被拉黑")
    def test_logout_positive(self, user_factory, setup_teardown_user, api_client):
        user = user_factory()

        with allure.step("1. 注册并登录拿到Token"):
            api_client.post("/api/v2/user/register", json=user)
            setup_teardown_user.append(user["username"])
            
            resp_login = api_client.post("/api/v2/user/login", json={"username": user["username"], "password": user["password"]})
            token = resp_login.json()["data"]["token"]
            headers = {"Authorization": f"Bearer {token}"}

        with allure.step("2. 发起注销请求"):
            resp_logout = api_client.post("/api/v2/user/logout", headers=headers)
            assert resp_logout.status_code == 200
            assert resp_logout.json().get("msg") == "注销成功"

        with allure.step("3. 核心验证：使用已注销token发帖，必须要被Reids黑名单拦截"):
            post_payload = {"title": "注销后发帖", "content": "这篇帖子不应该被发布"}
            resp_post = api_client.post("/api/v2/posts/create", json=post_payload, headers=headers)

            assert resp_post.status_code == 401
            assert "已在其他地方登出" in resp_post.json().get("detail", "")

    
    @allure.title("负向：无头/残缺Token登出防御")
    @pytest.mark.parametrize("header_value, expected_code", [
        (None,401),
        ("Bearer ", 401),
        ("FakeToken", 401)
    ])
    def test_logout_negative(self, api_client, header_value, expected_code):
        with allure.step(f"发送异常请求头: {header_value}"):
            headers = {"Authorization": header_value} if header_value is not None else {}
            resp = api_client.post("/api/v2/user/logout", headers=headers)

            assert resp.json().get("code") == expected_code
