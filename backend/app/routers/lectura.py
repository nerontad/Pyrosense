from fastapi import APIRouter, Depends
from app.schemas.lectura import LecturaResponse
from app.database.connection import execute_query
from app.routers.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/lecturas", tags=["Lecturas Sensores"])

@router.get("/{dispositivo_id}", response_model=List[LecturaResponse])
def obtener_lecturas(
    dispositivo_id: str,
    limite: int = 50,
    usuario=Depends(get_current_user)
):
    return execute_query(
        """SELECT l.* FROM lecturas_sensores l
           JOIN dispositivos_iot d ON d.id = l.dispositivo_id
           WHERE l.dispositivo_id = %s AND d.usuario_id = %s
           ORDER BY l.registrado_en DESC LIMIT %s""",
        (dispositivo_id, usuario["id"], limite),
        fetch=True
    )

@router.get("/{dispositivo_id}/ultima", response_model=Optional[LecturaResponse])
def obtener_ultima_lectura(
    dispositivo_id: str,
    usuario=Depends(get_current_user)
):
    from app.database.connection import execute_one
    return execute_one(
        """SELECT l.* FROM lecturas_sensores l
           JOIN dispositivos_iot d ON d.id = l.dispositivo_id
           WHERE l.dispositivo_id = %s AND d.usuario_id = %s
           ORDER BY l.registrado_en DESC LIMIT 1""",
        (dispositivo_id, usuario["id"])
    )