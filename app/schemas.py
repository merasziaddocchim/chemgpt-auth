from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserVerify(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
