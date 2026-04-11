from pydantic import BaseModel

class RegisterReq(BaseModel):
    username: str
    password: str
    email: str

class LoginReq(BaseModel):
    username: str
    password: str