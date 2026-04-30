import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.camara import CamaraCreate, CamaraResponse, CamaraUpdate
from app.database.connection import execute_query, execute_one
from app.routers.auth import get_current_user
from typing import List
from app.services.stream_service import iniciar_stream, detener_stream, streams_activos


router = APIRouter(prefix="/camaras", tags=["Cámaras"])

@router.post("/", response_model=CamaraResponse)
def crear_camara(data: CamaraCreate, usuario=Depends(get_current_user)):
    cam_id = str(uuid.uuid4())
    execute_query(
        """INSERT INTO camaras (id, usuario_id, ubicacion_id, nombre, url_rtsp)
           VALUES (%s, %s, %s, %s, %s)""",
        (cam_id, usuario["id"], data.ubicacion_id, data.nombre, data.url_rtsp)
    )
    return execute_one("SELECT * FROM camaras WHERE id = %s", (cam_id,))

@router.get("/", response_model=List[CamaraResponse])
def listar_camaras(usuario=Depends(get_current_user)):
    return execute_query(
        "SELECT * FROM camaras WHERE usuario_id = %s ORDER BY creado_en DESC",
        (usuario["id"],), fetch=True
    )

@router.get("/{cam_id}", response_model=CamaraResponse)
def obtener_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = execute_one(
        "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
        (cam_id, usuario["id"])
    )
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return cam

@router.patch("/{cam_id}", response_model=CamaraResponse)
def actualizar_camara(cam_id: str, data: CamaraUpdate, usuario=Depends(get_current_user)):
    cam = execute_one(
        "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
        (cam_id, usuario["id"])
    )
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if data.nombre is not None:
        execute_query("UPDATE camaras SET nombre = %s WHERE id = %s", (data.nombre, cam_id))
    if data.url_rtsp is not None:
        execute_query("UPDATE camaras SET url_rtsp = %s WHERE id = %s", (data.url_rtsp, cam_id))
    if data.activo is not None:
        execute_query("UPDATE camaras SET activo = %s WHERE id = %s", (data.activo, cam_id))
    return execute_one("SELECT * FROM camaras WHERE id = %s", (cam_id,))

@router.delete("/{cam_id}")
def eliminar_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = execute_one(
        "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
        (cam_id, usuario["id"])
    )
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    execute_query("DELETE FROM camaras WHERE id = %s", (cam_id,))
    return {"mensaje": "Cámara eliminada"}


@router.post("/{cam_id}/stream/iniciar")
def iniciar_stream_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = execute_one(
        "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
        (cam_id, usuario["id"])
    )
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if not cam["activo"]:
        raise HTTPException(status_code=400, detail="Cámara inactiva")
    iniciar_stream(cam_id, cam["url_rtsp"])
    return {"mensaje": f"Stream iniciado para cámara {cam['nombre']}"}

@router.post("/{cam_id}/stream/detener")
def detener_stream_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = execute_one(
        "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
        (cam_id, usuario["id"])
    )
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    detener_stream(cam_id)
    return {"mensaje": f"Stream detenido para cámara {cam['nombre']}"}

@router.get("/streams/activos")
def listar_streams_activos(usuario=Depends(get_current_user)):
    return {"streams_activos": streams_activos()}