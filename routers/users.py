from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from config import DEBUG
from dependencies import get_current_user_id
from database import friends as friendsdb
from database import pets as petsdb
from database.db import pool

router = APIRouter(tags=["users"])


@router.get("/")
async def read_root():
    return {"message": "DEBUG MODE" if DEBUG else "Hi nerd!"}


@router.get("/me")
async def me(user_id: Annotated[int, Depends(get_current_user_id)]):
    with pool.connection() as conn, conn.cursor() as cursor:
        friends = friendsdb.get_all_couples(cursor, user_id)
        pets = petsdb.get_all_pets(cursor, user_id)
    if friends is None:
        raise HTTPException(status_code=500, detail="Error to fetch friends")
    if pets is None:
        pets = []
    return {"user_id": user_id, "friends": friends, "pets": pets}
