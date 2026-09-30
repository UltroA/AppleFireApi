from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class UserReg(User):
    email: str


