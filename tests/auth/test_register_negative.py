import uuid
import pytest
import requests
import allure
from config.env_config import Config

# 每一个元组代表：（username, password, email，expected code，description）
REGISTRATION_DDT_POOL = [
    # 3-point BVA n n-1 n+1: password必须在8-16位，且包含大小写字母、数字和特殊字符
    ("invalid_user1_short", "A"*4 + "a1!", "invalid1@example.com", 400, "非法密码：8-1位，边界值校验"),
    ("valid_user1", "A"*5 + "a1!", "valid1@example.com", 200, "合法密码：8位加混合字符"),
    ("valid_user2", "A"*6 + "a1!", "valid2@example.com", 200, "合法密码：8+1位加混合字符"),
    ("valid_user3", "A"*12 + "a1!", "valid3@example.com", 200, "合法密码：16-1位加混合字符"),
    ("valid_user4", "A"*13 + "a1!", "valid4@example.com", 200, "合法密码：16位加混合字符"),
    ("invalid_user2_long", "A"*14 + "a1!", "invalid2@example.com", 400, "非法密码：16+1位，边界值校验"),

    # complexity checks: password必须包含大小写字母、数字和特殊字符
    ("invalid_user3_no_upper", "a"*8 + "1!", "invalid3@example.com", 400, "非法密码：无大写字母"),
    ("invalid_user4_no_lower", "A"*8 + "1!", "invalid4@example.com", 400, "非法密码：无小写字母"),
    ("invalid_user5_no_digit", "A"*8 + "a!", "invalid5@example.com", 400, "非法密码：无数字"),
    ("invalid_user6_no_special", "A"*8 + "a1!", "invalid6@example.com", 400, "非法密码：无特殊字符"),

    # username checks
    ("", "A"*8 + "a1!", "invalid7@example.com", 400, "非法用户名：空用户名"),

    # mail checks
    ("invalid_user8", "A"*8 + "a1!", "", 400, "非法邮箱：空邮箱"),
    ("invalid_user9", "A"*8 + "a1!", "invalid-email-format", 400, "非法邮箱：格式错误"),

]

@allure.epic("论坛系统测试")
@allure.feature("用户认证模块")
@allure.story("异常校验：DDT")
class TestUserRegisterNegative:

    @pytest.mark.parametrize("username, password, email, expected_code, description", REGISTRATION_DDT_POOL)
    def test_register_negative_rules(self, setup_teardown_user, username, password, email, expected_code, description):
        """
        利用参数化技术，批量验证后端拦截逻辑是否生效
        """
        allure.dynamic.title(f"注册异常校验: {description}")

        # 只有用户名不为空时才加 UUID，确保测试场景真实
        unique_name = f"{username}_{str(uuid.uuid4())[:8]}" if username != "" else ""

        payload = {
            "username": unique_name,
            "password": password,
            "email": email
        }

        with allure.step(f"执行异常数据测试：{description}"):
            resp = requests.post(f"{Config.BASE_URL}/api/v2/user/register", json=payload, timeout=5)
            res_json = resp.json()

            # 只有误操作注册成功时，才需要加入清理列表
            if res_json.get("code") == 200:
                setup_teardown_user.append(unique_name)

            # 断言：校验 code 和后端返回的 msg
            assert res_json.get("code") == expected_code, \
                f"失败！预期 {expected_code}，但返回 {res_json.get('code')}, 详情：{res_json.get('msg')}"
