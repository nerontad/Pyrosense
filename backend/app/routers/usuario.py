# Router de usuarios: gestionar perfil y configuración de canales de notificación
from fastapi import APIRouter, Depends
from app.schemas.usuario import UsuarioResponse
from app.repositories import usuario_repo
from app.routers.auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(usuario=Depends(get_current_user)):
    # Obtener datos del perfil del usuario autenticado
    return usuario


@router.patch("/me/telegram")
def actualizar_telegram(chat_id: str, usuario=Depends(get_current_user)):
    # Guardar chat_id de Telegram para notificaciones
    usuario_repo.actualizar_telegram(usuario["id"], chat_id)
    return {"mensaje": "Telegram configurado correctamente"}
