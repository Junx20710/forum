from pydantic import BaseModel, Field, ConfigDict

class PostCreateReq(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)