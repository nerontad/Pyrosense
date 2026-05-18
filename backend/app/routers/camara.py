# Router de cámaras: crear, listar, actualizar y eliminar cámaras RTSP
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.camara import CamaraCreate, CamaraResponse, CamaraUpdate
from app.repositories import camara_repo
from app.routers.auth import get_current_user
from app.services.stream_service import iniciar_stream, detener_stream, streams_activos
from typing import List

router = APIRouter(prefix="/camaras", tags=["Cámaras"])


@router.post("/", response_model=CamaraResponse)
def crear_camara(data: CamaraCreate, usuario=Depends(get_current_user)):
    # Crear nueva cámara e iniciar detección automática
    camara = camara_repo.crear(
        usuario["id"], data.ubicacion_id, data.nombre, data.url_rtsp
    )
    iniciar_stream(camara["id"], data.url_rtsp)
    return camara


@router.get("/", response_model=List[CamaraResponse])
def listar_camaras(usuario=Depends(get_current_user)):
    # Listar todas las cámaras del usuario
    return camara_repo.listar_por_usuario(usuario["id"])


@router.get("/{cam_id}", response_model=CamaraResponse)
def obtener_camara(cam_id: str, usuario=Depends(get_current_user)):
    # Obtener detalles de una cámara específica
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return cam


@router.patch("/{cam_id}", response_model=CamaraResponse)
def actualizar_camara(cam_id: str, data: CamaraUpdate, usuario=Depends(get_current_user)):
    # Actualizar configuración de cámara
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if data.nombre is not None:
        camara_repo.actualizar_nombre(cam_id, data.nombre)
    if data.url_rtsp is not None:
        camara_repo.actualizar_url(cam_id, data.url_rtsp)
        # Reiniciar stream con nueva URL
        detener_stream(cam_id)
        iniciar_stream(cam_id, data.url_rtsp)
    if data.activo is not None:
        camara_repo.actualizar_activo(cam_id, data.activo)
        if data.activo:
            cam_actual = camara_repo.obtener_por_id(cam_id)
            iniciar_stream(cam_id, cam_actual["url_rtsp"])
        else:
            detener_stream(cam_id)
    return camara_repo.obtener_por_id(cam_id)


@router.delete("/{cam_id}")
def eliminar_camara(cam_id: str, usuario=Depends(get_current_user)):
    # Eliminar cámara y detener detección
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    detener_stream(cam_id)
    camara_repo.eliminar(cam_id)
    return {"mensaje": "Cámara eliminada"}


@router.get("/streams/activos")
def listar_streams_activos(usuario=Depends(get_current_user)):
    # Listar todas las cámaras en detección activa
    return {"streams_activos": streams_activos()}
