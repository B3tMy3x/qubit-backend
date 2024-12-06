from db.connect import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import validates
import random
from sqlalchemy import Float

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_ip: Mapped[str] = mapped_column()
    assurance: Mapped[float] = mapped_column(Float, nullable=False)
    tickets = relationship("Ticket", back_populates="chat")

    @validates("assurance")
    def generate_assurance(self, key, value):
        if value is None:
            return random.uniform(0.02, 0.95)
        return value

    def __init__(self, user_ip: str, assurance: float = None):
        self.user_ip = user_ip
        self.assurance = assurance or random.uniform(0.02, 0.95)

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column()
    answer: Mapped[str] = mapped_column()
    date: Mapped[datetime] = mapped_column(DateTime)
    solved: Mapped[bool] = mapped_column()
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    chat = relationship("Chat", back_populates="tickets")
