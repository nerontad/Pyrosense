# Servicio de autenticación con Firebase: verificación de tokens y sincronización de usuarios
import firebase_admin
from firebase_admin import credentials, auth
from app.repositories import usuario_repo
import os
import json


def _inicializar_firebase():
    # Inicializar Firebase desde variables de entorno (producción) o archivo local
    if firebase_admin._apps:
        return

    firebase_creds_str = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_creds_str:
        # Producción: credenciales en variable de entorno
        creds_dict = json.loads(firebase_creds_str)
        cred = credentials.Certificate(creds_dict)
    else:
        # Desarrollo: credenciales en archivo local
        cred = credentials.Certificate("firebase_credentials.json")

    firebase_admin.initialize_app(cred)


_inicializar_firebase()


def verificar_token_firebase(id_token: str) -> dict | None:
    # Validar token JWT de Firebase
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print(f"Error verificando token Firebase: {e}")
        return None


def obtener_o_crear_usuario(firebase_uid: str, email: str, nombre: str = None) -> dict:
    # Obtener usuario del sistema o crear si no existe. Sincroniza con Firebase.
    usuario = usuario_repo.obtener_por_firebase_uid(firebase_uid)
    if usuario:
        return usuario

    usuario = usuario_repo.obtener_por_email(email)
    if usuario:
        usuario_repo.vincular_firebase_uid(email, firebase_uid)
        return usuario_repo.obtener_por_email(email)

    nombre_final = nombre or email.split("@")[0]
    return usuario_repo.crear(firebase_uid, email, nombre_final)
