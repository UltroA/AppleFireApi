from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

import uvicorn
import psycopg
import base64
import os

import database


app = FastAPI()



@app.get("/")
async def read_root():
    raise HTTPException(status_code=200, detail="Hi nerd!")


@app.post("/reg/")
async def reg_user(username: str, email: str, password: str):
    try:
        with psycopg.connect(dbname="postgres", user="postgres") as conn:
            with conn.cursor() as cursor:
                database.create_table_users(cursor)
                database.create_user(cursor, username, email,
                                     str(base64.b64encode(password.encode())))
                cursor.execute("SELECT * FROM users;")
                conn.commit()
        return {True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@app.post("/login/")
async def login_user(username: str, password: str):
    try:
        with psycopg.connect(dbname="postgres", user="postgres") as conn:
            with conn.cursor() as cursor:
                pwd = database.seach_by_name(cursor, username)
                if pwd == str(base64.b64encode(password.encode())):
                    return {True}
    except Exception as e:
        print(e)
        if DEBUG:
            return {False, e}
    raise HTTPException(status_code=403, detail="Wrong username or password")

if __name__ == "__main__":
    load_dotenv()
    DEBUG = bool(os.getenv("DEBUG"))
    if DEBUG:
        print("DEBUG MODE")
    uvicorn.run(app, host="0.0.0.0", port=8000)
