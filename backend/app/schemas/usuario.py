from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Esquema para creación de nuevo usuario
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telegram_chat_id: Optional[str] = None

# Esquema de respuesta con datos del usuario
class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    email: str
    telegram_chat_id: Optional[str] = None
    creado_en: datetime

# Esquema para solicitud de login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Esquema de respuesta con token de autenticación
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse