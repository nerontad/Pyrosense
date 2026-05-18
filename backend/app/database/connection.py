# Conexión a base de datos MySQL con pool de conexiones reutilizables
import mysql.connector
from mysql.connector import pooling
from app.config import get_settings

settings = get_settings()

# Pool de 5 conexiones para evitar crear nuevas conexiones cada vez
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

def get_connection():
    # Obtener conexión del pool
    return pool.get_connection()

def execute_query(query: str, params: tuple = None, fetch: bool = False):
    # Ejecutar INSERT, UPDATE, DELETE y retornar ID generado o datos si fetch=True
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

def execute_one(query: str, params: tuple = None):
    # Ejecutar SELECT y retornar un solo registro
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()