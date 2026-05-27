import mysql.connector
from mysql.connector import pooling
from app.config import get_settings

settings = get_settings()

# Pool de conexiones MySQL — se crea perezosamente la primera vez que se usa.
# Así el módulo se puede importar en tests sin requerir un MySQL en localhost.
_pool: pooling.MySQLConnectionPool | None = None


def _get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="detector_pool",
            pool_size=5,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            charset="utf8mb4",
        )
    return _pool


# Saca una conexión del pool (inicializándolo en el primer uso)
def get_connection():
    return _get_pool().get_connection()

# Ejecuta una query: SELECT (fetch=True) o INSERT/UPDATE/DELETE (devuelve lastrowid)
def execute_query(query: str, params: tuple = None, fetch: bool = False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

# Ejecuta una query y devuelve la primera fila (None si no hay resultados)
def execute_one(query: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
