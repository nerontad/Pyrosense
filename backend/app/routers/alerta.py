from fastapi import APIRouter, HTTPException, Depends
from app.schemas.alerta import AlertaResponse, AlertaDetalle
from app.routers.auth import get_current_user
from app.repositories import alerta_repo, video_alerta_repo
from typing import List

router = APIRouter(prefix="/alertas", tags=["Alertas"])

# Lista las alertas del usuario con su video adjunto (si existe)
@router.get("/", response_model=List[AlertaDetalle])
def listar_alertas(
    limite: int = 20,
    solo_pendientes: bool = False,
    usuario=Depends(get_current_user)
):
    alertas = alerta_repo.listar_por_usuario(usuario["id"], limite, solo_pendientes)
    # Adjunta el video correspondiente a cada alerta
    return [
        {**alerta, "video": video_alerta_repo.obtener_por_alerta(alerta["id"])}
        for alerta in alertas
    ]

# Devuelve una alerta concreta con su video
@router.get("/{alerta_id}", response_model=AlertaDetalle)
def obtener_alerta(alerta_id: str, usuario=Depends(get_current_user)):
    alerta = alerta_repo.obtener_por_id_y_usuario(alerta_id, usuario["id"])
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    video = video_alerta_repo.obtener_por_alerta(alerta["id"])
    return {**alerta, "video": video}

# Marca la alerta como revisada por el usuario
@router.patch("/{alerta_id}/revisar")
def marcar_revisada(alerta_id: str, usuario=Depends(get_current_user)):
    alerta = alerta_repo.obtener_por_id_y_usuario(alerta_id, usuario["id"])
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta_repo.marcar_revisada(alerta_id)
    return {"mensaje": "Alerta marcada como revisada"}
