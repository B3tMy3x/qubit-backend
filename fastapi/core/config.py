from os import getenv
from dotenv import load_dotenv

load_dotenv()


class AuthSettings:
    SECRET_KEY = getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE = 2  # hours


class BaseSettings:
    LINK = getenv("LINK")


class CORSSetting:
    pass