from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from jwt_auth import hash_password, verify_password, create_access_token
from db.models import User
from db import get_db
from routers import UserBase, UserResponse
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/ping")
async def read_root():
    return {"status": "fastapi service is running!"}


@router.post("/register")
async def register(user: UserBase, db: AsyncSession = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"auth": "registration is successful"}


@router.post("/login")
async def login(user: UserBase, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalars().first()
    if db_user is None or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    user_ip = request.client.host
    access_token = create_access_token(data={"sub": db_user.username}, ip=user_ip)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
