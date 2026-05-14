import uuid
from typing import Optional, List
from app.repositories.base import BaseRepository


class AlertaRepository(BaseRepository):
    tabla = "alertas"

    def crear(self, camara_id: str, tipo_id: int, confianza: float) -> str:
        alerta_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO alertas (id, camara_id, tipo_id, confianza)
               VALUES (%s, %s, %s, %s)""",
            (alerta_id, camara_id, tipo_id, confianza)
        )
        return alerta_id

    def listar_por_usuario(self, usuario_id: str, limite: int = 20,
                           solo_pendientes: bool = False) -> List[dict]:
        filtro = "AND a.revisado = 0" if solo_pendientes else ""
        return self._query(
            f"""SELECT a.* FROM alertas a
                JOIN camaras c ON c.id = a.camara_id
                WHERE c.usuario_id = %s {filtro}
                ORDER BY a.ocurrido_en DESC LIMIT %s""",
            (usuario_id, limite), fetch=True
        ) or []

    def obtener_por_id_y_usuario(self, alerta_id: str,
                                 usuario_id: str) -> Optional[dict]:
        return self._query_one(
            """SELECT a.* FROM alertas a
               JOIN camaras c ON c.id = a.camara_id
               WHERE a.id = %s AND c.usuario_id = %s""",
            (alerta_id, usuario_id)
        )

    def marcar_revisada(self, alerta_id: str) -> None:
        self._query(
            "UPDATE alertas SET revisado = 1 WHERE id = %s",
            (alerta_id,)
        )
