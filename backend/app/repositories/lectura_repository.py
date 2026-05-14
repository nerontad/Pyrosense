import uuid
from typing import Optional, List
from app.repositories.base import BaseRepository


class LecturaRepository(BaseRepository):
    tabla = "lecturas_sensores"

    def crear(self, dispositivo_id: str, temperatura: Optional[float],
              humedad: Optional[float], co2_ppm: Optional[float]) -> dict:
        lectura_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO lecturas_sensores
               (id, dispositivo_id, temperatura, humedad, co2_ppm)
               VALUES (%s, %s, %s, %s, %s)""",
            (lectura_id, dispositivo_id, temperatura, humedad, co2_ppm)
        )
        return self.obtener_por_id(lectura_id)

    def listar_por_dispositivo_y_usuario(self, dispositivo_id: str,
                                         usuario_id: str,
                                         limite: int = 50) -> List[dict]:
        return self._query(
            """SELECT l.* FROM lecturas_sensores l
               JOIN dispositivos_iot d ON d.id = l.dispositivo_id
               WHERE l.dispositivo_id = %s AND d.usuario_id = %s
               ORDER BY l.registrado_en DESC LIMIT %s""",
            (dispositivo_id, usuario_id, limite), fetch=True
        ) or []

    def ultima_por_dispositivo_y_usuario(self, dispositivo_id: str,
                                         usuario_id: str) -> Optional[dict]:
        return self._query_one(
            """SELECT l.* FROM lecturas_sensores l
               JOIN dispositivos_iot d ON d.id = l.dispositivo_id
               WHERE l.dispositivo_id = %s AND d.usuario_id = %s
               ORDER BY l.registrado_en DESC LIMIT 1""",
            (dispositivo_id, usuario_id)
        )
