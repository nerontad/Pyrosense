import uuid
from fastapi import APIRouter, Depends
from app.database.connection import execute_query, execute_one
from app.routers.auth import get_current_user
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
    return execute_query(
        "SELECT * FROM ubicaciones WHERE usuario_id = %s ORDER BY nombre ASC",
        (usuario["id"],),
        fetch=True
    )

# Crea una nueva ubicación para el usuario
@router.post("/", response_model=UbicacionResponse)
def crear_ubicacion(data: UbicacionCreate, usuario=Depends(get_current_user)):
    ubi_id = str(uuid.uuid4())
    execute_query(
        "INSERT INTO ubicaciones (id, usuario_id, nombre, descripcion) VALUES (%s, %s, %s, %s)",
        (ubi_id, usuario["id"], data.nombre, data.descripcion)
    )
    return execute_one("SELECT * FROM ubicaciones WHERE id = %s", (ubi_id,))

# Elimina una ubicación del usuario
@router.delete("/{ubi_id}")
def eliminar_ubicacion(ubi_id: str, usuario=Depends(get_current_user)):
    execute_query(
        "DELETE FROM ubicaciones WHERE id = %s AND usuario_id = %s",
        (ubi_id, usuario["id"])
    )
    return {"mensaje": "Ubicación eliminada"}
