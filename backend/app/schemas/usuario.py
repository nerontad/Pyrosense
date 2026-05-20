from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Datos necesarios para registrar un usuario
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telegram_chat_id: Optional[str] = None

# Datos de usuario devueltos al cliente
class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    email: str
    telegram_chat_id: Optional[str] = None
    creado_en: datetime

# Credenciales para iniciar sesión
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Respuesta exitosa de login: token + usuario
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
