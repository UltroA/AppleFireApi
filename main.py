import jwt
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from pwdlib import PasswordHash
from typing import Annotated
from datetime import datetime, timedelta, timezone


import uvicorn
import os

import models
import database

load_dotenv()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DB_DSN = os.getenv("DATABASE_URL", "dbname=postgres user=postgres")
SECRET_KEY = os.getenv("SECRET_KEY", "just_for_test")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pool = ConnectionPool(DB_DSN, open=False)
passwordHash = PasswordHash.recommended()
ANTI_TIME_HASH = passwordHash.hash("not-a-real-password")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    with pool.connection() as conn, conn.cursor() as cursor:
        database.create_table_users(cursor)
    yield
    pool.close()

app = FastAPI(lifespan=lifespan)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


@app.get("/")
async def read_root():
    return {"message": "DEBUG MODE" if DEBUG else "Hi nerd!"}


async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except:
        raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/reg/")
async def reg_user(user: models.UserReg):
    hashed_password = passwordHash.hash(user.password)

    with pool.connection() as conn, conn.cursor() as cursor:
        user_id = database.create_user(cursor, user.username, user.email.lower(), hashed_password)

    if user_id is None:
        raise HTTPException(status_code=409, detail="User already exists")

    return {"success": True, "userID": user_id}


@app.post("/token")
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with pool.connection() as conn, conn.cursor() as cursor:
        user_info = database.search_by_email(cursor, form_data.username.lower())
        id = user_info[0] if user_info else None
        stored_hash = user_info[1] if user_info else None
    valid = passwordHash.verify(form_data.password, stored_hash or ANTI_TIME_HASH)
    print(valid)
    if user_info is None or not valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"access_token": create_access_token(id), "token_type": "bearer"}


@app.get("/me")
async def me(user_id: Annotated[int, Depends(get_current_user_id)]):
    return {"user_id": user_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
