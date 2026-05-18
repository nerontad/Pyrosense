from fastapi import APIRouter, Depends
from app.repositories import ubicacion_repo
from app.routers.auth import get_current_user
from typing import List
from pydantic import BaseModel


# Modelos para crear y retornar ubicaciones
class UbicacionCreate(BaseModel):
    nombre: str
    descripcion: str = None


class UbicacionResponse(BaseModel):
    id: str
    nombre: str
    descripcion: str = None


# API para gestionar ubicaciones de dispositivos y cámaras
router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])


@router.get("/", response_model=List[UbicacionResponse])
def listar_ubicaciones(usuario=Depends(get_current_user)):
    # Lista todas las ubicaciones del usuario
    return ubicacion_repo.listar_por_usuario(usuario["id"])


@router.post("/", response_model=UbicacionResponse)
def crear_ubicacion(data: UbicacionCreate, usuario=Depends(get_current_user)):
    # Crea una nueva ubicación para organizar dispositivos y cámaras
    return ubicacion_repo.crear(usuario["id"], data.nombre, data.descripcion)


@router.delete("/{ubi_id}")
def eliminar_ubicacion(ubi_id: str, usuario=Depends(get_current_user)):
    # Elimina una ubicación del usuario
    ubicacion_repo.eliminar(ubi_id, usuario["id"])
    return {"mensaje": "Ubicación eliminada"}
