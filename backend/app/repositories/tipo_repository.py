from typing import List
from app.repositories.base import BaseRepository


class TipoDispositivoRepository(BaseRepository):
    tabla = "tipos_dispositivo"

    def listar_ordenados(self) -> List[dict]:
        return self._query(
            "SELECT * FROM tipos_dispositivo ORDER BY id ASC",
            fetch=True
        ) or []
