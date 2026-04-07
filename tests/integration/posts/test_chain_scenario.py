import pytest
import requests
import allure
from app.core.config import Config

@allure.epic("论坛核心业务链路验证")
@allure.feature("多用户社交互动链路")
class TestSocialChain:

    @allure.story("A发帖_B点赞_取消点赞_状态强一致性链路")
    def test_like_post_synchronization(self, user_factory, setup_teardown_user):
        # ==================== 1. 角色 A 准备与发帖 ====================
        with allure.step("1. 角色 A 注册并登录"):
            user_a = user_factory()
            requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=user_a)
            setup_teardown_user.append(user_a["username"])
            
            resp_a = requests.post(f"{Config.BASE_URL}/api/v2/user/login", json=user_a)
            token_a = resp_a.json()["data"]["token"]
            header_a = {"Authorization": f"Bearer {token_a}"}

        with allure.step("2. 角色 A 发布新帖子"):
            post_payload = {"title": "可以反复横跳的点赞测试帖",
                             "content": "测试 Toggle 逻辑"}
            resp_post = requests.post(
                f"{Config.BASE_URL}/api/v2/posts/create", 
                json=post_payload, headers=header_a
            )
            assert resp_post.status_code == 200, f"发帖失败，响应：{resp_post.text}"
            
            post_id = resp_post.json()["data"]["post_id"]

        # ==================== 2. 角色 B 介入 ====================
        with allure.step("3. 角色 B 注册并登录"):
            user_b = user_factory()
            requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=user_b)
            setup_teardown_user.append(user_b["username"])
            
            resp_b = requests.post(f"{Config.BASE_URL}/api/v2/user/login", json=user_b)
            token_b = resp_b.json()["data"]["token"]
            header_b = {"Authorization": f"Bearer {token_b}"}

        with allure.step("4. 角色 B 首次点赞帖子"):
            resp_like_1 = requests.post(
                f"{Config.BASE_URL}/api/v2/posts/{post_id}/like", 
                headers=header_b
            )
            assert resp_like_1.status_code == 200, f"点赞失败，响应：{resp_like_1.text}"
            assert resp_like_1.json().get("code") == 200
            assert resp_like_1.json().get("msg") == "点赞成功"

        with allure.step("5. 角色 B 再次点击点赞按钮 (期望：触发取消点赞)"):
            resp_like_2 = requests.post(
                f"{Config.BASE_URL}/api/v2/posts/{post_id}/like", 
                headers=header_b
            )
            assert resp_like_2.json().get("code") == 200
            assert resp_like_2.json().get("msg") == "取消点赞成功"

        # ==================== 3. 状态闭环验证 ====================
        with allure.step("6. 角色 A 查询列表，验证赞数一致性"):
            resp_list = requests.get(f"{Config.BASE_URL}/api/v2/posts/list", headers=header_a)
            posts = resp_list.json()["data"]
            
            target_post = next((p for p in posts if p["id"] == post_id), None)
            assert target_post is not None, "帖子丢失"
            
            assert target_post["likes_count"] == 0, f"数据不一致！期望 0，实际 {target_post['likes_count']}"