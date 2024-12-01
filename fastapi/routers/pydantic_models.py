from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

class TicketCreate(BaseModel):
    question: str
    answer: str
    solved: bool