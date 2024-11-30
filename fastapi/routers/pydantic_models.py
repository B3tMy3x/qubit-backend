from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str