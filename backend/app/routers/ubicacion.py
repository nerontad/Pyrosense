from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.repositories import ubicacion_repo
from typing import List
from pydantic import BaseModel

# Datos requeridos para crear una ubicación
class UbicacionCreate(BaseModel):
    nombre: str
    descripcion: str = None

# Estructura devuelta al consultar una ubicación
class UbicacionResponse(BaseModel):
    id: str
    nombre: str
    descripcion: str = None

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])

# Lista las ubicaciones del usuario actual
@router.get("/", response_model=List[UbicacionResponse])
def listar_ubicaciones(usuario=Depends(get_current_user)):
    return ubicacion_repo.listar_por_usuario(usuario["id"])

# Crea una nueva ubicación para el usuario
@router.post("/", response_model=UbicacionResponse)
def crear_ubicacion(data: UbicacionCreate, usuario=Depends(get_current_user)):
    return ubicacion_repo.crear(usuario["id"], data.nombre, data.descripcion)

# Elimina una ubicación del usuario
@router.delete("/{ubi_id}")
def eliminar_ubicacion(ubi_id: str, usuario=Depends(get_current_user)):
    ubicacion_repo.eliminar(ubi_id, usuario["id"])
    return {"mensaje": "Ubicación eliminada"}
