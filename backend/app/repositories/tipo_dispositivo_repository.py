from app.repositories.base_repository import BaseRepository


class TipoDispositivoRepository(BaseRepository):
    def listar_todos(self):
        # Retorna catálogo de todos los tipos de dispositivos disponibles
        return self._query(
            "SELECT * FROM tipos_dispositivo ORDER BY id ASC",
            fetch=True
        )
