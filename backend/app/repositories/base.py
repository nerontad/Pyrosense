"""
Patrón Repository — clase base abstracta.

Encapsula el acceso a datos para que la capa de routers/servicios no
contenga SQL embebido. Cada entidad del dominio tiene su propio repositorio
que hereda de BaseRepository y expone métodos semánticos
(p. ej. obtener_por_id, listar_por_usuario) en lugar de queries crudas.
"""
from abc import ABC
from typing import Optional, List
from app.database.connection import execute_query, execute_one


class BaseRepository(ABC):
    """Clase base para todos los repositorios.

    Subclases deben definir el atributo `tabla` con el nombre de la tabla
    SQL correspondiente a la entidad.
    """
    tabla: str = ""

    def _query(self, sql: str, params: tuple = None, fetch: bool = False):
        return execute_query(sql, params, fetch=fetch)

    def _query_one(self, sql: str, params: tuple = None) -> Optional[dict]:
        return execute_one(sql, params)

    def obtener_por_id(self, entidad_id) -> Optional[dict]:
        return self._query_one(
            f"SELECT * FROM {self.tabla} WHERE id = %s",
            (entidad_id,)
        )

    def listar_todos(self) -> List[dict]:
        return self._query(
            f"SELECT * FROM {self.tabla}",
            fetch=True
        ) or []

    def eliminar(self, entidad_id) -> None:
        self._query(
            f"DELETE FROM {self.tabla} WHERE id = %s",
            (entidad_id,)
        )
