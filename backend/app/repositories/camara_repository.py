import uuid
from app.repositories.base_repository import BaseRepository


class CamaraRepository(BaseRepository):
    def crear(self, usuario_id: str, ubicacion_id: str, nombre: str, url_rtsp: str):
        # Crea una nueva cámara RTSP para vigilancia
        cam_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO camaras (id, usuario_id, ubicacion_id, nombre, url_rtsp)
               VALUES (%s, %s, %s, %s, %s)""",
            (cam_id, usuario_id, ubicacion_id, nombre, url_rtsp)
        )
        return self.obtener_por_id(cam_id)

    def obtener_por_id(self, cam_id: str):
        # Obtiene datos de una cámara por ID
        return self._one(
            "SELECT * FROM camaras WHERE id = %s",
            (cam_id,)
        )

    def obtener_por_id_y_usuario(self, cam_id: str, usuario_id: str):
        # Obtiene cámara verificando que pertenece al usuario
        return self._one(
            "SELECT * FROM camaras WHERE id = %s AND usuario_id = %s",
            (cam_id, usuario_id)
        )

    def listar_por_usuario(self, usuario_id: str):
        # Lista todas las cámaras del usuario ordenadas por fecha
        return self._query(
            "SELECT * FROM camaras WHERE usuario_id = %s ORDER BY creado_en DESC",
            (usuario_id,),
            fetch=True
        )

    def listar_activas(self):
        # Obtiene todas las cámaras activas del sistema para procesamiento
        return self._query(
            "SELECT id, url_rtsp, nombre FROM camaras WHERE activo = 1",
            fetch=True
        )

    def actualizar_nombre(self, cam_id: str, nombre: str):
        # Cambia el nombre de una cámara
        self._query(
            "UPDATE camaras SET nombre = %s WHERE id = %s",
            (nombre, cam_id)
        )

    def actualizar_url(self, cam_id: str, url_rtsp: str):
        # Actualiza la URL RTSP de la cámara
        self._query(
            "UPDATE camaras SET url_rtsp = %s WHERE id = %s",
            (url_rtsp, cam_id)
        )

    def actualizar_activo(self, cam_id: str, activo: bool):
        # Activa o desactiva el procesamiento de una cámara
        self._query(
            "UPDATE camaras SET activo = %s WHERE id = %s",
            (activo, cam_id)
        )

    def eliminar(self, cam_id: str):
        # Elimina una cámara del sistema
        self._query(
            "DELETE FROM camaras WHERE id = %s",
            (cam_id,)
        )

    def obtener_info_telegram(self, camara_id: str):
        # Obtiene info necesaria para enviar alertas de cámara por Telegram
        return self._one(
            """SELECT u.telegram_chat_id, ub.nombre as ubicacion
               FROM camaras c
               JOIN usuarios u ON u.id = c.usuario_id
               JOIN ubicaciones ub ON ub.id = c.ubicacion_id
               WHERE c.id = %s""",
            (camara_id,)
        )
