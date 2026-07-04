from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(..., max_length=1000)
