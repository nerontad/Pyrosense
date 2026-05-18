# Funciones de seguridad: hash de contraseñas y manejo de tokens JWT
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()

# Contexto para hashear contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Generar hash seguro de la contraseña
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # Verificar que la contraseña en texto plano coincida con el hash
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    # Crear token JWT con información del usuario y expiración
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> dict:
    # Decodificar y validar token JWT. Retorna None si es inválido
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None