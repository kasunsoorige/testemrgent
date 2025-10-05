from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: str = "Hey there! I am using PayPhone."

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = None

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    password_hash: str
    is_online: bool = False
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

class UserResponse(UserBase):
    id: str
    is_online: bool
    last_seen: datetime
    created_at: datetime

    class Config:
        allow_population_by_field_name = True