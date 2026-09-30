from pydantic import BaseModel, EmailStr, Field, field_validator


class UserReg(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if sum(c.isdigit() for c in v) < 3:
            raise ValueError('Password must be at least 3 digits')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserLog(BaseModel):
    email: EmailStr
    password: str
