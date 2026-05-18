import uuid
from app.repositories.base_repository import BaseRepository


class VideoAlertaRepository(BaseRepository):
    def crear(self, alerta_id: str, datos_video: dict) -> str:
        # Registra video clip capturado durante una alerta de incendio
        video_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO videos_alerta
               (id, alerta_id, ruta_archivo, duracion_seg, tamano_bytes)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                video_id,
                alerta_id,
                datos_video["ruta_archivo"],
                datos_video["duracion_seg"],
                datos_video["tamano_bytes"]
            )
        )
        return video_id

    def obtener_por_alerta(self, alerta_id: str):
        # Obtiene el video asociado a una alerta
        return self._one(
            "SELECT * FROM videos_alerta WHERE alerta_id = %s",
            (alerta_id,)
        )

    def marcar_enviado_telegram(self, alerta_id: str):
        # Marca que el video de la alerta fue enviado por Telegram
        self._query(
            "UPDATE videos_alerta SET enviado_telegram = 1 WHERE alerta_id = %s",
            (alerta_id,)
        )
