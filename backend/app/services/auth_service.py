import uuid
from app.database.connection import execute_query, execute_one
from app.utils.security import hash_password, verify_password, create_access_token

# Crea un usuario nuevo en la BD (devuelve None si el email ya existe)
def registrar_usuario(nombre: str, email: str, password: str, telegram_chat_id: str = None):
    existente = execute_one(
        "SELECT id FROM usuarios WHERE email = %s",
        (email,)
    )
    if existente:
        return None

    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)

    execute_query(
        """INSERT INTO usuarios (id, nombre, email, password_hash, telegram_chat_id)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, nombre, email, password_hash, telegram_chat_id)
    )
    return execute_one("SELECT * FROM usuarios WHERE id = %s", (user_id,))

# Valida credenciales y devuelve un token JWT + datos del usuario
def login_usuario(email: str, password: str):
    usuario = execute_one(
        "SELECT * FROM usuarios WHERE email = %s",
        (email,)
    )
    if not usuario:
        return None
    if not verify_password(password, usuario["password_hash"]):
        return None

    token = create_access_token({"sub": usuario["id"], "email": usuario["email"]})
    return {"token": token, "usuario": usuario}

# Busca un usuario por su ID
def obtener_usuario_por_id(user_id: str):
    return execute_one(
        "SELECT id, nombre, email, telegram_chat_id, creado_en FROM usuarios WHERE id = %s",
        (user_id,)
    )
