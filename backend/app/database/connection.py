import mysql.connector
from mysql.connector import pooling
from app.config import get_settings

settings = get_settings()

# Pool de conexiones MySQL reutilizables (más eficiente que abrir una por petición)
pool = pooling.MySQLConnectionPool(
    pool_name="detector_pool",
    pool_size=5,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
    charset="utf8mb4"
)

# Saca una conexión del pool
def get_connection():
    return pool.get_connection()

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
