from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from database import users as usersdb
from database import friends as friendsdb
from database.db import pool
from routers import auth, users, friends


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    with pool.connection() as conn, conn.cursor() as cursor:
        usersdb.create_table_users(cursor)
        friendsdb.create_table_couples(cursor)
    yield
    pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(friends.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
