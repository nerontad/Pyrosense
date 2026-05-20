from fastapi import APIRouter, HTTPException, Depends
from app.schemas.usuario import UsuarioResponse
from app.database.connection import execute_query, execute_one
from app.routers.auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Devuelve el perfil del usuario autenticado
@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(usuario=Depends(get_current_user)):
    return usuario

# Guarda el chat_id de Telegram del usuario
@router.patch("/me/telegram")
def actualizar_telegram(chat_id: str, usuario=Depends(get_current_user)):
    execute_query(
        "UPDATE usuarios SET telegram_chat_id = %s WHERE id = %s",
        (chat_id, usuario["id"])
    )
    return {"mensaje": "Telegram configurado correctamente"}
