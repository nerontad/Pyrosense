from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dispositivo import DispositivoCreate, DispositivoResponse, DispositivoUpdate
from app.repositories import dispositivo_repo
from app.routers.auth import get_current_user
from typing import List

# API para gestionar dispositivos IoT del usuario
router = APIRouter(prefix="/dispositivos", tags=["Dispositivos IoT"])


@router.post("/", response_model=DispositivoResponse)
def crear_dispositivo(data: DispositivoCreate, usuario=Depends(get_current_user)):
    # Crea un nuevo dispositivo IoT asociado al usuario autenticado
    return dispositivo_repo.crear(
        usuario["id"], data.ubicacion_id, data.tipo_id, data.nombre
    )


@router.get("/", response_model=List[DispositivoResponse])
def listar_dispositivos(usuario=Depends(get_current_user)):
    # Lista todos los dispositivos del usuario autenticado
    return dispositivo_repo.listar_por_usuario(usuario["id"])


@router.get("/{disp_id}", response_model=DispositivoResponse)
def obtener_dispositivo(disp_id: str, usuario=Depends(get_current_user)):
    # Obtiene detalles de un dispositivo específico si pertenece al usuario
    disp = dispositivo_repo.obtener_por_id_y_usuario(disp_id, usuario["id"])
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return disp


@router.patch("/{disp_id}", response_model=DispositivoResponse)
def actualizar_dispositivo(disp_id: str, data: DispositivoUpdate, usuario=Depends(get_current_user)):
    # Actualiza nombre o estado activo del dispositivo
    disp = dispositivo_repo.obtener_por_id_y_usuario(disp_id, usuario["id"])
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if data.nombre is not None:
        dispositivo_repo.actualizar_nombre(disp_id, data.nombre)
    if data.activo is not None:
        dispositivo_repo.actualizar_activo(disp_id, data.activo)
    return dispositivo_repo.obtener_por_id(disp_id)


@router.delete("/{disp_id}")
def eliminar_dispositivo(disp_id: str, usuario=Depends(get_current_user)):
    # Elimina un dispositivo IoT del usuario
    disp = dispositivo_repo.obtener_por_id_y_usuario(disp_id, usuario["id"])
    if not disp:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    dispositivo_repo.eliminar(disp_id)
    return {"mensaje": "Dispositivo eliminado"}
