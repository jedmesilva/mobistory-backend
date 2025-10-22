from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema para resposta de token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload do token JWT"""
    sub: Optional[str] = None  # user_id
