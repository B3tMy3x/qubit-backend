from fastapi import APIRouter


router = APIRouter(prefix="/api")


@router.get("/ping")
async def read_root():
    return {"status": "fastapi service is running!"}
