from fastapi import APIRouter, Depends
from app.repositories import tipo_dispositivo_repo
from app.routers.auth import get_current_user

# API para obtener catálogo de tipos de dispositivos disponibles
router = APIRouter(prefix="/tipos-dispositivo", tags=["Tipos"])


@router.get("/")
def listar_tipos(usuario=Depends(get_current_user)):
    # Retorna el listado de tipos de dispositivo disponibles en el sistema
    return tipo_dispositivo_repo.listar_todos()
