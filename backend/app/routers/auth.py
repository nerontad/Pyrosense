# Router de autenticación: verificar tokens Firebase y sincronizar usuarios
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.firebase_service import verificar_token_firebase, obtener_o_crear_usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Dependencia: validar token JWT de Firebase y retornar usuario
    token = credentials.credentials
    decoded = verificar_token_firebase(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    usuario = obtener_o_crear_usuario(
        firebase_uid=decoded["uid"],
        email=decoded.get("email", ""),
        nombre=decoded.get("name")
    )
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario

@router.post("/sync")
def sync_usuario(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Sincronizar usuario de Firebase: obtener o crear en BD
    token = credentials.credentials
    decoded = verificar_token_firebase(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    usuario = obtener_o_crear_usuario(
        firebase_uid=decoded["uid"],
        email=decoded.get("email", ""),
        nombre=decoded.get("name")
    )
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "telegram_chat_id": usuario.get("telegram_chat_id")
    }

@router.get("/me")
def me(usuario=Depends(get_current_user)):
    # Obtener perfil del usuario autenticado
    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "telegram_chat_id": usuario.get("telegram_chat_id")
    }