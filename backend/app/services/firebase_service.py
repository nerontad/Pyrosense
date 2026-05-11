import firebase_admin
from firebase_admin import credentials, auth
from app.database.connection import execute_one, execute_query
import uuid
import os
import json

def _inicializar_firebase():
    if firebase_admin._apps:
        return
    
    firebase_creds_str = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_creds_str:
        # Producción: leer desde variable de entorno
        creds_dict = json.loads(firebase_creds_str)
        cred = credentials.Certificate(creds_dict)
    else:
        # Desarrollo local: leer desde archivo
        cred = credentials.Certificate("firebase_credentials.json")
    
    firebase_admin.initialize_app(cred)

_inicializar_firebase()

def verificar_token_firebase(id_token: str) -> dict | None:
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print(f"Error verificando token Firebase: {e}")
        return None

def obtener_o_crear_usuario(firebase_uid: str, email: str, nombre: str = None) -> dict:
    usuario = execute_one(
        "SELECT * FROM usuarios WHERE firebase_uid = %s",
        (firebase_uid,)
    )
    if usuario:
        return usuario

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

    user_id = str(uuid.uuid4())
    nombre_final = nombre or email.split("@")[0]
    execute_query(
        """INSERT INTO usuarios (id, firebase_uid, nombre, email, password_hash)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, firebase_uid, nombre_final, email, "firebase_auth")
    )
    return execute_one("SELECT * FROM usuarios WHERE id = %s", (user_id,))