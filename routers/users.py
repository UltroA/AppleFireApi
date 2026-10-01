from typing import Annotated
from fastapi import APIRouter, Depends

from config import DEBUG
from dependencies import get_current_user_id

router = APIRouter(tags=["users"])


@router.get("/")
async def read_root():
    return {"message": "DEBUG MODE" if DEBUG else "Hi nerd!"}


@router.get("/me")
async def me(user_id: Annotated[int, Depends(get_current_user_id)]):
    return {"user_id": user_id}
