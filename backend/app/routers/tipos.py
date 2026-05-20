from fastapi import APIRouter, Depends
from app.database.connection import execute_query
from app.routers.auth import get_current_user

router = APIRouter(prefix="/tipos-dispositivo", tags=["Tipos"])

# Lista el catálogo de tipos de dispositivo IoT
@router.get("/")
def listar_tipos(usuario=Depends(get_current_user)):
    return execute_query(
        "SELECT * FROM tipos_dispositivo ORDER BY id ASC",
        fetch=True
    )
