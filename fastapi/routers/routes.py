from fastapi import Depends, HTTPException, Request, status, Header
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from jwt_auth import hash_password, verify_password, create_access_token, verify_token
from db.models import User, Chat, Ticket
from db import get_db
from routers import UserBase, UserResponse, TicketCreate
from fastapi import APIRouter
from datetime import datetime


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


@router.post("/ticket")
async def post_ticket(
    ticket_data: TicketCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_ip = request.client.host

    chat = await db.execute(select(Chat).where(Chat.user_ip == user_ip))
    chat = chat.scalars().first()

    if not chat:
        chat = Chat(user_ip=user_ip)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

    ticket = Ticket(
        question=ticket_data.question,
        answer=ticket_data.answer,
        date=datetime.now(),
        solved=ticket_data.solved,
        chat_id=chat.id,
    )
    db.add(ticket)
    await db.commit()

    return {"msg": "Ticket successfully added"}


@router.get("/chats")
async def get_chats(
    request: Request,
    token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    await verify_token(request, token)

    result = await db.execute(select(Chat))
    chats = result.scalars().all()
    return chats


@router.get("/chats/{chat_id}")
async def get_tickets(
    chat_id: int,
    request: Request,
    token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    await verify_token(request, token)

    result = await db.execute(select(Ticket).where(Ticket.chat_id == chat_id))
    tickets = result.scalars().all()
    return tickets


@router.get("/tickets/unsolved")
async def get_unsolved_tickets(
    request: Request,
    token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    await verify_token(request, token)

    result = await db.execute(select(Ticket).where(Ticket.solved == False))
    unsolved_tickets = result.scalars().all()
    return unsolved_tickets


@router.post("/tickets/{ticket_id}")
async def solve_ticket(
    ticket_id: int,
    request: Request,
    token: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    await verify_token(request, token)

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    ticket.solved = True
    await db.commit()

    return {"msg": "Successfully solved the ticket"}
