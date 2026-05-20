from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()

# Contexto bcrypt para hashear y verificar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Devuelve el hash bcrypt de una contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Comprueba si la contraseña en claro coincide con el hash
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Genera un JWT firmado con la clave secreta y la expiración configurada
def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

# Decodifica un JWT y devuelve sus claims (None si es inválido)
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
