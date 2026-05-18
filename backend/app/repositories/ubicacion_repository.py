import uuid
from app.repositories.base_repository import BaseRepository


class UbicacionRepository(BaseRepository):
    def crear(self, usuario_id: str, nombre: str, descripcion: str = None):
        # Crea una nueva ubicación para organizar dispositivos y cámaras
        ubi_id = str(uuid.uuid4())
        self._query(
            "INSERT INTO ubicaciones (id, usuario_id, nombre, descripcion) VALUES (%s, %s, %s, %s)",
            (ubi_id, usuario_id, nombre, descripcion)
        )
        return self._one(
            "SELECT * FROM ubicaciones WHERE id = %s",
            (ubi_id,)
        )

    def listar_por_usuario(self, usuario_id: str):
        # Lista todas las ubicaciones del usuario ordenadas alfabéticamente
        return self._query(
            "SELECT * FROM ubicaciones WHERE usuario_id = %s ORDER BY nombre ASC",
            (usuario_id,),
            fetch=True
        )

    def eliminar(self, ubi_id: str, usuario_id: str):
        # Elimina una ubicación verificando que pertenece al usuario
        self._query(
            "DELETE FROM ubicaciones WHERE id = %s AND usuario_id = %s",
            (ubi_id, usuario_id)
        )
