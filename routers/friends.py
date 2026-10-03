from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from config import DEBUG
from dependencies import get_current_user_id
from database.db import pool
from database import friends as friendsdb
from database import users as usersdb

router = APIRouter(tags=["friends"])


@router.post("/add_friend")
async def add_friend(user_id: Annotated[int, Depends(get_current_user_id)], email: str):
    with pool.connection() as conn, conn.cursor() as cursor:
        user_info = usersdb.search_by_email(cursor, email.lower())
        if user_info is None:
            raise HTTPException(status_code=404, detail="User not found")
        father_id = user_info[0]
        couple_id = friendsdb.create_couple(cursor, user_id, father_id)

    return {"success": True, "coupleId": couple_id}
