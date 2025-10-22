from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base schema para User"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para criar usuário"""
    password: str


class UserUpdate(BaseModel):
    """Schema para atualizar usuário"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """Schema do usuário no banco"""
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class User(UserInDB):
    """Schema público do usuário (sem campos sensíveis)"""
    pass


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str
