import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dispositivo import DispositivoCreate, DispositivoResponse, DispositivoUpdate
from app.database.connection import execute_query, execute_one, execute_query as eq
from app.routers.auth import get_current_user
from typing import List

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos IoT"])

# Crea un nuevo dispositivo IoT para el usuario actual
@router.post("/", response_model=DispositivoResponse)
def crear_dispositivo(data: DispositivoCreate, usuario=Depends(get_current_user)):
    disp_id = str(uuid.uuid4())
    execute_query(
        """INSERT INTO dispositivos_iot (id, usuario_id, ubicacion_id, tipo_id, nombre)
           VALUES (%s, %s, %s, %s, %s)""",
        (disp_id, usuario["id"], data.ubicacion_id, data.tipo_id, data.nombre)
    )
    return execute_one("SELECT * FROM dispositivos_iot WHERE id = %s", (disp_id,))

# Lista los dispositivos del usuario actual
@router.get("/", response_model=List[DispositivoResponse])
def listar_dispositivos(usuario=Depends(get_current_user)):
    return execute_query(
        "SELECT * FROM dispositivos_iot WHERE usuario_id = %s ORDER BY creado_en DESC",
        (usuario["id"],), fetch=True
    )

# Devuelve un dispositivo concreto del usuario
@router.get("/{disp_id}", response_model=DispositivoResponse)
def obtener_dispositivo(disp_id: str, usuario=Depends(get_current_user)):
    disp = execute_one(
        "SELECT * FROM dispositivos_iot WHERE id = %s AND usuario_id = %s",
        (disp_id, usuario["id"])
    )
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return disp

# Actualiza el nombre o el estado activo de un dispositivo
@router.patch("/{disp_id}", response_model=DispositivoResponse)
def actualizar_dispositivo(disp_id: str, data: DispositivoUpdate, usuario=Depends(get_current_user)):
    disp = execute_one(
        "SELECT * FROM dispositivos_iot WHERE id = %s AND usuario_id = %s",
        (disp_id, usuario["id"])
    )
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if data.nombre is not None:
        execute_query("UPDATE dispositivos_iot SET nombre = %s WHERE id = %s", (data.nombre, disp_id))
    if data.activo is not None:
        execute_query("UPDATE dispositivos_iot SET activo = %s WHERE id = %s", (data.activo, disp_id))
    return execute_one("SELECT * FROM dispositivos_iot WHERE id = %s", (disp_id,))

# Elimina un dispositivo del usuario
@router.delete("/{disp_id}")
def eliminar_dispositivo(disp_id: str, usuario=Depends(get_current_user)):
    disp = execute_one(
        "SELECT * FROM dispositivos_iot WHERE id = %s AND usuario_id = %s",
        (disp_id, usuario["id"])
    )
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    execute_query("DELETE FROM dispositivos_iot WHERE id = %s", (disp_id,))
    return {"mensaje": "Dispositivo eliminado"}
