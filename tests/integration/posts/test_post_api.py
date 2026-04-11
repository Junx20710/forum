import pytest
import allure




@allure.feature("发帖业务模块")
class TestPostDynamic:

    # DDT POOL(title, content, token_type, expected_code, description)
    

    @allure.story("动态链路：从注册到发帖的全生命周期")
    def test_create_dynamic_post(self, user_factory, setup_teardown_user, api_client):
        # 准备数据并注册
        user = user_factory()
        api_client.post("/api/v2/user/register", json=user)
        setup_teardown_user.append(user["username"])


        # 登录并拿token
        login_resp = api_client.post("/api/v2/user/login", 
                                   json={"username": user["username"], "password": user["password"]})
        token = login_resp.json()["data"]["token"]

        # 动态发帖
        post_data = {
            "title": f"{user['username'][-4:]}的测试帖子",
            "content": "这是一篇自动生成的测试帖子"
        }
        headers = {"Authorization": f"Bearer {token}"}
        with allure.step("发送发帖请求"):
            resp = api_client.post("/api/v2/posts/create", 
                                 json=post_data, headers=headers)

        assert resp.json().get("code") == 200

    POST_DDT_POOL = [
        ("A"*101, "正常内容", "valid", 400, "边界值：标题超长"),
        ("正常标题", "正常内容", "invalid", 401, "等价类：伪造的无效token"),
        ("   ", "   ", "valid", 400, "错误推测：标题和内容全为空格"),
    ]


    @allure.story("异常用例测试")
    @pytest.mark.parametrize("title, content, token_type, expected_code, description", POST_DDT_POOL)
    def test_post_negative(self, user_factory, setup_teardown_user, api_client, title, content, token_type, expected_code, description):
        """
        利用数据驱动验证发帖接口的边界值与鉴权拦截逻辑
        """
        allure.dynamic.title(f"发帖拦截校验：{description}")
        # 根据用例要求决定是否发真token
        token = "fake_and_invalid_token_string_eyJhb..."
        if token_type == "valid":
            user = user_factory()
            # 注册并加进清理队列
            api_client.post("/api/v2/user/register", json=user)
            setup_teardown_user.append(user["username"])

            # 登录，且成功才会拿真token
            login_resp = api_client.post("/api/v2/user/login",
                                        json={"username": user["username"], "password": user["password"]} 
            )
            login_data = login_resp.json()
            if login_resp.status_code == 200 and "data" in login_data:
                token = login_data["data"]["token"]
            else:
                pytest.fail(f"测试前置条件不满足：无法返回有效token，返回： {login_data}")

        # 发送异常请求
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"title": title, "content": content}

        with allure.step(f"发送破坏性请求:{description}"):
            resp = api_client.post("/api/v2/posts/create",
                                json=payload, headers=headers,
                                timeout=5)
        

        res_json = resp.json()
        actual_code = res_json.get("code") or resp.status_code
        assert actual_code == expected_code, \
            f"拦截失败！返回预期返回码 {expected_code}，实际返回: {actual_code}"

    


        


