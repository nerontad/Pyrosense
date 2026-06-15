from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.repositories import tipo_dispositivo_repo

router = APIRouter(prefix="/tipos-dispositivo", tags=["Tipos"])

# Lista el catálogo de tipos de dispositivo IoT
@router.get("/")
def listar_tipos(usuario=Depends(get_current_user)):
    return tipo_dispositivo_repo.listar_todos()
