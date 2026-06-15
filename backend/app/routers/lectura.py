from fastapi import APIRouter, Depends
from app.schemas.lectura import LecturaResponse
from app.routers.auth import get_current_user
from app.repositories import lectura_repo
from typing import List, Optional

router = APIRouter(prefix="/lecturas", tags=["Lecturas Sensores"])

# Devuelve el histórico de lecturas de un dispositivo (limitado)
@router.get("/{dispositivo_id}", response_model=List[LecturaResponse])
def obtener_lecturas(
    dispositivo_id: str,
    limite: int = 50,
    usuario=Depends(get_current_user)
):
    return lectura_repo.listar_por_dispositivo(dispositivo_id, usuario["id"], limite)

# Devuelve solo la última lectura del dispositivo
@router.get("/{dispositivo_id}/ultima", response_model=Optional[LecturaResponse])
def obtener_ultima_lectura(
    dispositivo_id: str,
    usuario=Depends(get_current_user)
):
    return lectura_repo.ultima_por_dispositivo(dispositivo_id, usuario["id"])
