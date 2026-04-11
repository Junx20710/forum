import uuid

class DataFactory:
    @staticmethod
    def build_user():
        """全量复用的造数引擎"""
        unique_id = uuid.uuid4().hex[:6]
        username = f"user_{unique_id}"
        return {
            "username": username,
            "password": "Password123!",
            "email": f"{username}@test.com" 
        }