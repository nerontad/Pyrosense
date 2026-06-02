import base64
import hashlib
from urllib.parse import urlsplit, urlunsplit
from cryptography.fernet import Fernet, InvalidToken
from app.config import get_settings

settings = get_settings()

# Prefijo que marca un valor como cifrado (distingue de cámaras legacy en texto plano)
_PREFIJO = "enc:"
# Texto con el que se enmascara la contraseña al mostrarla en el frontend
MASCARA = "••••••"


# Deriva una clave Fernet estable a partir de SECRET_KEY. Así no hace falta una variable de entorno nueva para la clave de cifrado, 
# y basta con cambiar SECRET_KEY para invalidar todos los datos cifrados por si se sospecha que la clave fue comprometida.
def _fernet() -> Fernet:
    clave = hashlib.sha256(settings.secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(clave))


# Cifra una URL RTSP para guardarla en la base de datos. Si ya viene cifrada, la devuelve sin volver a cifrar.
def cifrar_url(url: str) -> str:
    if not url or url.startswith(_PREFIJO):
        return url
    token = _fernet().encrypt(url.encode()).decode()
    return _PREFIJO + token


# Descifra una URL RTSP para uso interno (ffmpeg). Si el valor viene en texto plano (cámara antigua), lo devuelve tal cual.
def descifrar_url(valor: str) -> str:
    if not valor or not valor.startswith(_PREFIJO):
        return valor  # legacy: texto plano, compatibilidad hacia atrás
    try:
        return _fernet().decrypt(valor[len(_PREFIJO):].encode()).decode()
    except InvalidToken:
        # Clave incorrecta o dato corrupto: no exponer el token cifrado
        return ""


# Oculta la contraseña de una URL RTSP para enviarla al frontend.
def enmascarar_url(url: str) -> str:
    if not url:
        return url
    try:
        partes = urlsplit(url)
        if partes.password:
            usuario = partes.username or ""
            host = partes.hostname or ""
            puerto = f":{partes.port}" if partes.port else ""
            netloc = f"{usuario}:{MASCARA}@{host}{puerto}"
            return urlunsplit((partes.scheme, netloc, partes.path, partes.query, partes.fragment))
        return url
    except Exception:
        return url


# Indica si una URL recibida del frontend trae la contraseña enmascarada (es decir, el usuario NO escribió una contraseña nueva y no hay que tocarla).
def esta_enmascarada(url: str) -> bool:
    return bool(url) and MASCARA in url
