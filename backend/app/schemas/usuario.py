from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telegram_chat_id: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    email: str
    telegram_chat_id: Optional[str] = None
    creado_en: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse