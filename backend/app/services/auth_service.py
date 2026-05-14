from app.repositories import usuario_repo
from app.utils.security import hash_password, verify_password, create_access_token


def registrar_usuario(nombre: str, email: str, password: str,
                      telegram_chat_id: str = None):
    """Registra un nuevo usuario. Retorna None si el email ya existe."""
    if usuario_repo.obtener_por_email(email):
        return None
    return usuario_repo.crear(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password),
        telegram_chat_id=telegram_chat_id
    )


def login_usuario(email: str, password: str):
    """Verifica credenciales y retorna {token, usuario} o None."""
    usuario = usuario_repo.obtener_por_email(email)
    if not usuario or not verify_password(password, usuario["password_hash"]):
        return None
    token = create_access_token({
        "sub": usuario["id"],
        "email": usuario["email"]
    })
    return {"token": token, "usuario": usuario}


def obtener_usuario_por_id(user_id: str):
    return usuario_repo.obtener_publico_por_id(user_id)
