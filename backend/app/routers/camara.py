from fastapi import APIRouter, HTTPException, Depends
from app.schemas.camara import CamaraCreate, CamaraResponse, CamaraUpdate
from app.routers.auth import get_current_user
from app.repositories import camara_repo
from app.services.stream_service import iniciar_stream, detener_stream, streams_activos
from app.utils.crypto_rtsp import cifrar_url, descifrar_url, enmascarar_url, esta_enmascarada
from typing import List

router = APIRouter(prefix="/camaras", tags=["Cámaras"])


# Prepara una cámara para enviarla al frontend: la URL RTSP sale enmascarada
def _vista_publica(camara: dict) -> dict:
    cam = dict(camara)
    cam["url_rtsp"] = enmascarar_url(descifrar_url(cam.get("url_rtsp", "")))
    return cam

# Registra una cámara y arranca su stream de detección
@router.post("/", response_model=CamaraResponse)
def crear_camara(data: CamaraCreate, usuario=Depends(get_current_user)):
    # La URL se guarda cifrada en la BD; el stream usa la original en claro
    camara = camara_repo.crear(
        usuario["id"], data.ubicacion_id, data.nombre, cifrar_url(data.url_rtsp)
    )
    # Lanza el stream automáticamente al crear la cámara
    iniciar_stream(camara["id"], data.url_rtsp)
    return _vista_publica(camara)

# Lista las cámaras del usuario actual
@router.get("/", response_model=List[CamaraResponse])
def listar_camaras(usuario=Depends(get_current_user)):
    camaras = camara_repo.listar_por_usuario(usuario["id"])
    return [_vista_publica(c) for c in camaras]

# Devuelve una cámara concreta del usuario
@router.get("/{cam_id}", response_model=CamaraResponse)
def obtener_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return _vista_publica(cam)

# Actualiza nombre / URL / estado y reinicia el stream si es necesario
@router.patch("/{cam_id}", response_model=CamaraResponse)
def actualizar_camara(cam_id: str, data: CamaraUpdate, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    if data.nombre is not None:
        camara_repo.actualizar_nombre(cam_id, data.nombre)
    # Solo se cambia la URL si el usuario escribió una nueva (no la enmascarada que
    # le mostramos). Así editar el nombre no borra la contraseña real de la cámara.
    if data.url_rtsp is not None and not esta_enmascarada(data.url_rtsp):
        camara_repo.actualizar_url(cam_id, cifrar_url(data.url_rtsp))
        # Reinicia el stream con la nueva URL en claro
        detener_stream(cam_id)
        iniciar_stream(cam_id, data.url_rtsp)
    if data.activo is not None:
        camara_repo.actualizar_activo(cam_id, data.activo)
        # Arranca o detiene el stream según el nuevo estado
        if data.activo:
            cam_actual = camara_repo.obtener_por_id(cam_id)
            iniciar_stream(cam_id, descifrar_url(cam_actual["url_rtsp"]))
        else:
            detener_stream(cam_id)
    return _vista_publica(camara_repo.obtener_por_id(cam_id))

# Elimina la cámara y detiene su stream
@router.delete("/{cam_id}")
def eliminar_camara(cam_id: str, usuario=Depends(get_current_user)):
    cam = camara_repo.obtener_por_id_y_usuario(cam_id, usuario["id"])
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    detener_stream(cam_id)
    camara_repo.eliminar(cam_id)
    return {"mensaje": "Cámara eliminada"}

# Devuelve los IDs de los streams actualmente activos
@router.get("/streams/activos")
def listar_streams_activos(usuario=Depends(get_current_user)):
    return {"streams_activos": streams_activos()}
