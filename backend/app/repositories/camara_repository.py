import uuid
from typing import Optional, List
from app.repositories.base import BaseRepository


class CamaraRepository(BaseRepository):
    tabla = "camaras"

    def crear(self, usuario_id: str, ubicacion_id: int,
              nombre: str, url_rtsp: str) -> dict:
        cam_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO camaras
               (id, usuario_id, ubicacion_id, nombre, url_rtsp)
               VALUES (%s, %s, %s, %s, %s)""",
            (cam_id, usuario_id, ubicacion_id, nombre, url_rtsp)
        )
        return self.obtener_por_id(cam_id)

    def listar_por_usuario(self, usuario_id: str) -> List[dict]:
        return self._query(
            "SELECT * FROM camaras WHERE usuario_id = %s "
            "ORDER BY creado_en DESC",
            (usuario_id,), fetch=True
        ) or []

    def obtener_por_id_y_usuario(self, cam_id: str,
                                 usuario_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
            (cam_id, usuario_id)
        )

    def obtener_url_rtsp(self, cam_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT url_rtsp FROM camaras WHERE id = %s",
            (cam_id,)
        )

    def obtener_con_destinatario_telegram(self, cam_id: str) -> Optional[dict]:
        """Devuelve datos de la cámara junto al chat_id de Telegram del dueño
        y el nombre de la ubicación — usado por el motor de alertas."""
        return self._query_one(
            """SELECT u.telegram_chat_id, ub.nombre as ubicacion
               FROM camaras c
               JOIN usuarios u ON u.id = c.usuario_id
               JOIN ubicaciones ub ON ub.id = c.ubicacion_id
               WHERE c.id = %s""",
            (cam_id,)
        )

    def actualizar_nombre(self, cam_id: str, nombre: str) -> None:
        self._query(
            "UPDATE camaras SET nombre = %s WHERE id = %s",
            (nombre, cam_id)
        )

    def actualizar_url_rtsp(self, cam_id: str, url_rtsp: str) -> None:
        self._query(
            "UPDATE camaras SET url_rtsp = %s WHERE id = %s",
            (url_rtsp, cam_id)
        )

    def actualizar_activo(self, cam_id: str, activo: bool) -> None:
        self._query(
            "UPDATE camaras SET activo = %s WHERE id = %s",
            (activo, cam_id)
        )
