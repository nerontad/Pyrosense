from fastapi import APIRouter, HTTPException, Depends
from app.schemas.camara import CamaraCreate, CamaraResponse, CamaraUpdate
from app.repositories import camara_repo
from app.routers.auth import get_current_user
from typing import List
from app.services.stream_service import iniciar_stream, detener_stream, streams_activos


router = APIRouter(prefix="/camaras", tags=["Cámaras"])

@router.post("/", response_model=CamaraResponse)
def crear_camara(data: CamaraCreate, usuario=Depends(get_current_user)):
    return camara_repo.crear(
        usuario_id=usuario["id"],
        ubicacion_id=data.ubicacion_id,
        nombre=data.nombre,
        url_rtsp=data.url_rtsp
    )

@router.get("/", response_model=List[CamaraResponse])
def listar_camaras(usuario=Depends(get_current_user)):
    return camara_repo.listar_por_usuario(usuario["id"])

@router.get("/{cam_id}", response_model=CamaraResponse)
def obtener_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return cam

@router.patch("/{cam_id}", response_model=CamaraResponse)
def actualizar_camara(cam_id: str, data: CamaraUpdate, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if data.nombre is not None:
        camara_repo.actualizar_nombre(cam_id, data.nombre)
    if data.url_rtsp is not None:
        camara_repo.actualizar_url_rtsp(cam_id, data.url_rtsp)
    if data.activo is not None:
        camara_repo.actualizar_activo(cam_id, data.activo)
    return camara_repo.obtener_por_id(cam_id)

@router.delete("/{cam_id}")
def eliminar_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    camara_repo.eliminar(cam_id)
    return {"mensaje": "Cámara eliminada"}


@router.post("/{cam_id}/stream/iniciar")
def iniciar_stream_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if not cam["activo"]:
        raise HTTPException(status_code=400, detail="Cámara inactiva")
    iniciar_stream(cam_id, cam["url_rtsp"])
    return {"mensaje": f"Stream iniciado para cámara {cam['nombre']}"}

@router.post("/{cam_id}/stream/detener")
def detener_stream_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    detener_stream(cam_id)
    return {"mensaje": f"Stream detenido para cámara {cam['nombre']}"}

@router.get("/streams/activos")
def listar_streams_activos(usuario=Depends(get_current_user)):
    return {"streams_activos": streams_activos()}
