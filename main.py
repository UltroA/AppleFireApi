from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

import uvicorn
import psycopg
import os

import models
import database

app = FastAPI()

load_dotenv()
DEBUG = bool(os.getenv("DEBUG"))


@app.get("/")
async def read_root():
    return {"DEBUG MODE" if DEBUG else "Hi nerd!"}


@app.post("/reg/")
async def reg_user(user: models.UserReg):
    if not (3 <= len(user.username) < 16):
        raise HTTPException(status_code=413, detail="Username must be less than 16 characters or more than 3")
    if not ((6 < len(user.email) < 32)
            and "@" in user.email
            and "." in user.email):
        raise HTTPException(status_code=413, detail="Email must be between 6 and 20")
    if not (sum(1 for char in user.password if char.isdigit()) >= 3
            and sum(1 for char in user.password if char.isalpha()) >= 3
            and sum(1 for char in user.password if char.isupper()) >= 1):
        raise HTTPException(status_code=413, detail="Password must be at least 6 characters long and have 3 numbers "
                                                    "in it")
    try:
        with psycopg.connect(dbname="postgres", user="postgres") as conn:
            with conn.cursor() as cursor:
                if database.create_table_users(cursor):
                    print("SYSTEM: CREATED TABLE USERS")

                database.create_user(cursor, user)
                cursor.execute("SELECT * FROM users;")
                conn.commit()
        return {True}
    except Exception:
        raise HTTPException(status_code=400, detail="User already exists")


@app.post("/login/")
async def login_user(user: models.User):
    try:
        with psycopg.connect(dbname="postgres", user="postgres") as conn:
            with conn.cursor() as cursor:
                pwd = database.seach_by_name(cursor, user.username)
                if pwd == user.password:
                    return {True}
    except Exception as e:
        print(e)
        if DEBUG:
            return {False, e}
    raise HTTPException(status_code=403, detail="Wrong username or password")


if __name__ == "__main__":
    if DEBUG:
        with psycopg.connect(dbname="postgres", user="postgres") as conn:
            with conn.cursor() as cursor:
                database.drop_table(cursor, "users")
        print("DEBUG MODE")
    uvicorn.run(app, host="0.0.0.0", port=8000)
