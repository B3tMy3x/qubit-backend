import os
from dotenv import load_dotenv

load_dotenv()


class AuthSettings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE = 2  # hours


class BaseSettings:
    LINK = os.getenv("DATABASE_URL")


class GPT:
    CONNECTION = "123"


class GEMINI:
    CONNECTION = "345"


class Model:
    MODEL: GPT | GEMINI = GPT
