from fastapi import APIRouter, Depends
from app.schemas.lectura import LecturaResponse
from app.repositories import lectura_repo
from app.routers.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/lecturas", tags=["Lecturas Sensores"])

@router.get("/{dispositivo_id}", response_model=List[LecturaResponse])
def obtener_lecturas(
    dispositivo_id: str,
    limite: int = 50,
    usuario=Depends(get_current_user)
):
    return lectura_repo.listar_por_dispositivo_y_usuario(
        dispositivo_id, usuario["id"], limite
    )

@router.get("/{dispositivo_id}/ultima", response_model=Optional[LecturaResponse])
def obtener_ultima_lectura(
    dispositivo_id: str,
    usuario=Depends(get_current_user)
):
    return lectura_repo.ultima_por_dispositivo_y_usuario(
        dispositivo_id, usuario["id"]
    )
