from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from pwdlib import PasswordHash

import uvicorn
import os

import models
import database

load_dotenv()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DB_DSN = os.getenv("DATABASE_URL", "dbname=postgres user=postgres")


pool = ConnectionPool(DB_DSN, open=False)
passwordHash = PasswordHash.recommended()
ANTI_TIME_HASH = passwordHash.hash("not-a-real-password")


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    with pool.connection() as conn, conn.cursor() as cursor:
        database.create_table_users(cursor)
    yield
    pool.close()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "DEBUG MODE" if DEBUG else "Hi nerd!"}


@app.post("/reg/")
async def reg_user(user: models.UserReg):
    hashed_password = passwordHash.hash(user.password)

    with pool.connection() as conn, conn.cursor() as cursor:
        user_id = database.create_user(cursor, user.username, user.email.lower(), hashed_password)

    if user_id is None:
        raise HTTPException(status_code=409, detail="User already exists")

    return {"success": True, "userID": user_id}


@app.post("/login/")
async def login_user(user: models.UserLog):
    with pool.connection() as conn, conn.cursor() as cursor:
        user_info = database.search_by_email(cursor, user.email.lower())
        if user_info is None:
            raise HTTPException(status_code=401, detail="Invalid email")
        id = user_info[0]
        stored_hash = user_info[1]
    valid = passwordHash.verify(user.password, stored_hash or ANTI_TIME_HASH)

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"success": True, "UserID": id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
