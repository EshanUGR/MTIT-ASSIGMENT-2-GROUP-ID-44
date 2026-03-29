from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    age: int
    gender: str
    address: str

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    role: str
    user: UserResponse


class DeleteResponse(BaseModel):
    message: str
    id: int