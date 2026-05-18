from app.database.connection import execute_query, execute_one


class BaseRepository:
    """Clase base del patrón Repository.

    Encapsula el acceso a la BD para que los routers y services no
    dependan directamente de execute_query/execute_one. Cualquier
    repositorio concreto hereda de aquí y expone métodos de dominio
    (crear, listar, obtener_por_id, ...) en vez de SQL crudo.
    """

    def _query(self, sql: str, params: tuple = None, fetch: bool = False):
        # Ejecuta una consulta SQL (SELECT con fetch=True, INSERT/UPDATE/DELETE con fetch=False)
        return execute_query(sql, params, fetch=fetch)

    def _one(self, sql: str, params: tuple = None):
        # Ejecuta una consulta y retorna una única fila
        return execute_one(sql, params)
