import uuid
from typing import Optional
from app.repositories.base import BaseRepository


class VideoAlertaRepository(BaseRepository):
    tabla = "videos_alerta"

    def crear(self, alerta_id: str, ruta_archivo: str,
              duracion_seg: int, tamano_bytes: int) -> str:
        video_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO videos_alerta
               (id, alerta_id, ruta_archivo, duracion_seg, tamano_bytes)
               VALUES (%s, %s, %s, %s, %s)""",
            (video_id, alerta_id, ruta_archivo, duracion_seg, tamano_bytes)
        )
        return video_id

    def obtener_por_alerta(self, alerta_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT * FROM videos_alerta WHERE alerta_id = %s",
            (alerta_id,)
        )

    def marcar_enviado_telegram(self, alerta_id: str) -> None:
        self._query(
            "UPDATE videos_alerta SET enviado_telegram = 1 WHERE alerta_id = %s",
            (alerta_id,)
        )
