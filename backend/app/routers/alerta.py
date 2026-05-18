# Router de alertas: listar, obtener y revisar alertas de incendio detectadas
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.alerta import AlertaResponse, AlertaDetalle
from app.repositories import alerta_repo, video_alerta_repo
from app.routers.auth import get_current_user
from typing import List

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/", response_model=List[AlertaDetalle])
def listar_alertas(
    limite: int = 20,
    solo_pendientes: bool = False,
    usuario=Depends(get_current_user)
):
    # Listar alertas del usuario con opción de filtrar solo las no revisadas
    alertas = alerta_repo.listar_por_usuario(
        usuario["id"], limite=limite, solo_pendientes=solo_pendientes
    )
    resultado = []
    for alerta in alertas:
        video = video_alerta_repo.obtener_por_alerta(alerta["id"])
        resultado.append({**alerta, "video": video})
    return resultado


@router.get("/{alerta_id}", response_model=AlertaDetalle)
def obtener_alerta(alerta_id: str, usuario=Depends(get_current_user)):
    # Obtener detalles completos de una alerta con su video
    alerta = alerta_repo.obtener_por_id_y_usuario(alerta_id, usuario["id"])
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    video = video_alerta_repo.obtener_por_alerta(alerta["id"])
    return {**alerta, "video": video}


@router.patch("/{alerta_id}/revisar")
def marcar_revisada(alerta_id: str, usuario=Depends(get_current_user)):
    # Marcar alerta como revisada por el usuario
    alerta = alerta_repo.obtener_por_id_y_usuario(alerta_id, usuario["id"])
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta_repo.marcar_revisada(alerta_id)
    return {"mensaje": "Alerta marcada como revisada"}
