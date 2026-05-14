import uuid
from typing import Optional, List
from app.repositories.base import BaseRepository


class DispositivoRepository(BaseRepository):
    tabla = "dispositivos_iot"

    def crear(self, usuario_id: str, ubicacion_id: int,
              tipo_id: int, nombre: str) -> dict:
        disp_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO dispositivos_iot
               (id, usuario_id, ubicacion_id, tipo_id, nombre)
               VALUES (%s, %s, %s, %s, %s)""",
            (disp_id, usuario_id, ubicacion_id, tipo_id, nombre)
        )
        return self.obtener_por_id(disp_id)

    def listar_por_usuario(self, usuario_id: str) -> List[dict]:
        return self._query(
            "SELECT * FROM dispositivos_iot WHERE usuario_id = %s "
            "ORDER BY creado_en DESC",
            (usuario_id,), fetch=True
        ) or []

    def obtener_por_id_y_usuario(self, disp_id: str,
                                 usuario_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT * FROM dispositivos_iot WHERE id = %s AND usuario_id = %s",
            (disp_id, usuario_id)
        )

    def existe_activo(self, disp_id: str) -> bool:
        result = self._query_one(
            "SELECT id FROM dispositivos_iot WHERE id = %s AND activo = 1",
            (disp_id,)
        )
        return result is not None

    def actualizar_nombre(self, disp_id: str, nombre: str) -> None:
        self._query(
            "UPDATE dispositivos_iot SET nombre = %s WHERE id = %s",
            (nombre, disp_id)
        )

    def actualizar_activo(self, disp_id: str, activo: bool) -> None:
        self._query(
            "UPDATE dispositivos_iot SET activo = %s WHERE id = %s",
            (activo, disp_id)
        )
