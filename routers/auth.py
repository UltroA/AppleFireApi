from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from database import users as usersdb
import models
from database.db import pool
from security import password_hash, ANTI_TIME_HASH, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/reg/")
async def reg_user(user: models.UserReg):
    hashed_password = password_hash.hash(user.password)

    with pool.connection() as conn, conn.cursor() as cursor:
        user_id = usersdb.create_user(cursor, user.username, user.email.lower(), hashed_password)

    if user_id is None:
        raise HTTPException(status_code=409, detail="User already exists")

    return {"success": True, "userID": user_id}


@router.post("/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with pool.connection() as conn, conn.cursor() as cursor:
        user_info = usersdb.search_by_email(cursor, form_data.username.lower())

    user_id = user_info[0] if user_info else None
    stored_hash = user_info[1] if user_info else None

    valid = password_hash.verify(form_data.password, stored_hash or ANTI_TIME_HASH)
    if user_info is None or not valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"access_token": create_access_token(user_id), "token_type": "bearer"}
