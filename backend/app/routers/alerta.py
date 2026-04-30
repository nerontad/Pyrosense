from fastapi import APIRouter, HTTPException, Depends
from app.schemas.alerta import AlertaResponse, AlertaDetalle
from app.database.connection import execute_query, execute_one
from app.routers.auth import get_current_user
from typing import List

router = APIRouter(prefix="/alertas", tags=["Alertas"])

@router.get("/", response_model=List[AlertaDetalle])
def listar_alertas(
    limite: int = 20,
    solo_pendientes: bool = False,
    usuario=Depends(get_current_user)
):
    filtro = "AND a.revisado = 0" if solo_pendientes else ""
    alertas = execute_query(
        f"""SELECT a.* FROM alertas a
            JOIN camaras c ON c.id = a.camara_id
            WHERE c.usuario_id = %s {filtro}
            ORDER BY a.ocurrido_en DESC LIMIT %s""",
        (usuario["id"], limite),
        fetch=True
    )
    resultado = []
    for alerta in alertas:
        video = execute_one(
            "SELECT * FROM videos_alerta WHERE alerta_id = %s",
            (alerta["id"],)
        )
        resultado.append({**alerta, "video": video})
    return resultado

@router.get("/{alerta_id}", response_model=AlertaDetalle)
def obtener_alerta(alerta_id: str, usuario=Depends(get_current_user)):
    alerta = execute_one(
        """SELECT a.* FROM alertas a
           JOIN camaras c ON c.id = a.camara_id
           WHERE a.id = %s AND c.usuario_id = %s""",
        (alerta_id, usuario["id"])
    )
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    video = execute_one(
        "SELECT * FROM videos_alerta WHERE alerta_id = %s",
        (alerta["id"],)
    )
    return {**alerta, "video": video}

@router.patch("/{alerta_id}/revisar")
def marcar_revisada(alerta_id: str, usuario=Depends(get_current_user)):
    alerta = execute_one(
        """SELECT a.* FROM alertas a
           JOIN camaras c ON c.id = a.camara_id
           WHERE a.id = %s AND c.usuario_id = %s""",
        (alerta_id, usuario["id"])
    )
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    execute_query(
        "UPDATE alertas SET revisado = 1 WHERE id = %s",
        (alerta_id,)
    )
    return {"mensaje": "Alerta marcada como revisada"}