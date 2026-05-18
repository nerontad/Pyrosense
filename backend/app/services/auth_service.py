# Servicio de autenticación: registrar, login y obtener datos de usuario
from app.repositories import usuario_repo
from app.utils.security import hash_password, verify_password, create_access_token


def registrar_usuario(nombre: str, email: str, password: str, telegram_chat_id: str = None):
    # Registrar nuevo usuario. Retorna None si email ya existe
    if usuario_repo.obtener_por_email(email):
        return None
    password_hash = hash_password(password)
    return usuario_repo.crear_local(nombre, email, password_hash, telegram_chat_id)


def login_usuario(email: str, password: str):
    # Validar credenciales y retornar token JWT si son correctas
    usuario = usuario_repo.obtener_por_email(email)
    if not usuario:
        return None
    if not verify_password(password, usuario["password_hash"]):
        return None
    token = create_access_token({"sub": usuario["id"], "email": usuario["email"]})
    return {"token": token, "usuario": usuario}


def obtener_usuario_por_id(user_id: str):
    # Obtener datos del usuario por su ID
    return usuario_repo.obtener_por_id(user_id)
