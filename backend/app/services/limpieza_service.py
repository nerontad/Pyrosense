"""Job en background que borra lecturas de sensores antiguas.

Cumple RNF04: las lecturas con más de DIAS_RETENCION días en la BD se
eliminan automáticamente. Corre en un hilo daemon que se despierta cada
INTERVALO_S y aplica el DELETE.
"""

import threading
import time
from app.database.connection import execute_query

# Cuánto tiempo se conservan las lecturas (en días)
DIAS_RETENCION = 90

# Frecuencia con la que se ejecuta la limpieza (24 horas)
INTERVALO_S = 24 * 60 * 60

# Flag para poder parar el hilo al cerrar la app
_activo = False
_hilo: threading.Thread | None = None


def purgar_lecturas_antiguas() -> int:
    """Elimina lecturas con `registrado_en` anterior a hace DIAS_RETENCION días.

    Devuelve el número de filas borradas (o 0 si hubo error).
    Es público para poder llamarlo manualmente desde un endpoint o un test.
    """
    try:
        # cursor.rowcount queda disponible por debajo; el helper devuelve
        # lastrowid. Para saber cuántos borramos, hacemos un COUNT previo.
        contados = execute_query(
            """SELECT COUNT(*) AS n FROM lecturas_sensores
               WHERE registrado_en < (NOW() - INTERVAL %s DAY)""",
            (DIAS_RETENCION,),
            fetch=True,
        )
        borrar = contados[0]["n"] if contados else 0

        execute_query(
            """DELETE FROM lecturas_sensores
               WHERE registrado_en < (NOW() - INTERVAL %s DAY)""",
            (DIAS_RETENCION,),
        )
        print(f"Limpieza: {borrar} lecturas con más de {DIAS_RETENCION} días borradas")
        return borrar
    except Exception as e:
        print(f"Limpieza: error al purgar lecturas antiguas: {e}")
        return 0


def _bucle():
    # Ejecuta una vez al arrancar y luego cada INTERVALO_S
    while _activo:
        purgar_lecturas_antiguas()
        # Dormita en tramos cortos para responder rápido al apagado
        dormido = 0
        while _activo and dormido < INTERVALO_S:
            time.sleep(5)
            dormido += 5


def iniciar_limpieza():
    """Arranca el hilo de limpieza si aún no está corriendo."""
    global _activo, _hilo
    if _activo:
        return
    _activo = True
    _hilo = threading.Thread(target=_bucle, daemon=True, name="limpieza-lecturas")
    _hilo.start()
    print(f"Limpieza programada: cada {INTERVALO_S}s, retención {DIAS_RETENCION} días")


def detener_limpieza():
    """Detiene el bucle de limpieza al cerrar la app."""
    global _activo
    _activo = False
