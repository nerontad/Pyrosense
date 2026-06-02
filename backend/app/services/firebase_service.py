import firebase_admin
from firebase_admin import credentials, auth
from app.database.connection import execute_one, execute_query
import uuid
import os
import json

# Inicializa el SDK de Firebase Admin con credenciales de env o archivo local.
# Si no hay credenciales (p.ej. en desarrollo local) la app NO se cae: solo
# queda deshabilitada la verificación de tokens.
def _inicializar_firebase():
    if firebase_admin._apps:
        return

    try:
        firebase_creds_str = os.getenv("FIREBASE_CREDENTIALS")
        if firebase_creds_str:
            # Producción: credenciales en variable de entorno
            creds_dict = json.loads(firebase_creds_str)
            cred = credentials.Certificate(creds_dict)
        else:
            # Desarrollo local: archivo en disco
            cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase NO inicializado (sin credenciales): {e}. "
              f"La autenticación con Firebase no funcionará hasta configurarlas.")

_inicializar_firebase()

# Verifica un ID token de Firebase y devuelve sus claims
def verificar_token_firebase(id_token: str) -> dict | None:
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print(f"Error verificando token Firebase: {e}")
        return None

# Busca al usuario por UID o email, y si no existe lo crea en la BD local
def obtener_o_crear_usuario(firebase_uid: str, email: str, nombre: str = None) -> dict:
    # Caso 1: ya existe con ese firebase_uid
    usuario = execute_one(
        "SELECT * FROM usuarios WHERE firebase_uid = %s",
        (firebase_uid,)
    )
    if usuario:
        return usuario

    # Caso 2: existe con el mismo email pero sin uid (legacy) → vincular
    usuario = execute_one(
        "SELECT * FROM usuarios WHERE email = %s",
        (email,)
    )
    if usuario:
        execute_query(
            "UPDATE usuarios SET firebase_uid = %s WHERE email = %s",
            (firebase_uid, email)
        )
        return execute_one("SELECT * FROM usuarios WHERE email = %s", (email,))

    # Caso 3: usuario nuevo → insertar
    user_id = str(uuid.uuid4())
    nombre_final = nombre or email.split("@")[0]
    execute_query(
        """INSERT INTO usuarios (id, firebase_uid, nombre, email, password_hash)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, firebase_uid, nombre_final, email, "firebase_auth")
    )
    return execute_one("SELECT * FROM usuarios WHERE id = %s", (user_id,))
