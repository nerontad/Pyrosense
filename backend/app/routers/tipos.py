from fastapi import APIRouter, Depends
from app.repositories import tipo_repo
from app.routers.auth import get_current_user

router = APIRouter(prefix="/tipos-dispositivo", tags=["Tipos"])

@router.get("/")
def listar_tipos(usuario=Depends(get_current_user)):
    return tipo_repo.listar_ordenados()
