from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
import jwt
from core import AuthSettings


SECRET_KEY = AuthSettings.SECRET_KEY
ALGORITHM = AuthSettings.ALGORITHM
ACCESS_TOKEN_EXPIRE = AuthSettings.ACCESS_TOKEN_EXPIRE

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, ip: str):
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE),
            "ip": ip,
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(request: Request, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_ip = payload.get("ip")
        if token_ip != request.client.host:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="IP address mismatch"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def verify_token(request: Request, token: str):
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])

        token_ip = payload.get("ip")
        if token_ip != request.client.host:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="IP address mismatch"
            )

        user_username = payload.get("sub")

        if not user_username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token data invalid"
            )

        return {"id": user_username}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
