import uuid
from app.repositories.base_repository import BaseRepository


class DispositivoRepository(BaseRepository):
    def crear(self, usuario_id: str, ubicacion_id: str, tipo_id: int, nombre: str):
        # Crea nuevo dispositivo IoT (sensor) para el usuario
        disp_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO dispositivos_iot (id, usuario_id, ubicacion_id, tipo_id, nombre)
               VALUES (%s, %s, %s, %s, %s)""",
            (disp_id, usuario_id, ubicacion_id, tipo_id, nombre)
        )
        return self.obtener_por_id(disp_id)

    def obtener_por_id(self, disp_id: str):
        # Obtiene información completa de un dispositivo
        return self._one(
            "SELECT * FROM dispositivos_iot WHERE id = %s",
            (disp_id,)
        )

    def obtener_por_id_y_usuario(self, disp_id: str, usuario_id: str):
        # Obtiene dispositivo verificando propiedad del usuario
        return self._one(
            "SELECT * FROM dispositivos_iot WHERE id = %s AND usuario_id = %s",
            (disp_id, usuario_id)
        )

    def obtener_activo_por_id(self, disp_id: str):
        # Obtiene solo dispositivos activos para procesamiento
        return self._one(
            "SELECT id FROM dispositivos_iot WHERE id = %s AND activo = 1",
            (disp_id,)
        )

    def listar_por_usuario(self, usuario_id: str):
        # Lista todos los dispositivos del usuario
        return self._query(
            "SELECT * FROM dispositivos_iot WHERE usuario_id = %s ORDER BY creado_en DESC",
            (usuario_id,),
            fetch=True
        )

    def actualizar_nombre(self, disp_id: str, nombre: str):
        # Cambia el nombre mostrado del dispositivo
        self._query(
            "UPDATE dispositivos_iot SET nombre = %s WHERE id = %s",
            (nombre, disp_id)
        )

    def actualizar_activo(self, disp_id: str, activo: bool):
        # Activa o desactiva la recepción de datos del dispositivo
        self._query(
            "UPDATE dispositivos_iot SET activo = %s WHERE id = %s",
            (activo, disp_id)
        )

    def eliminar(self, disp_id: str):
        # Elimina el dispositivo del sistema
        self._query(
            "DELETE FROM dispositivos_iot WHERE id = %s",
            (disp_id,)
        )
