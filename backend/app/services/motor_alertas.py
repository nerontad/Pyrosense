import uuid
import asyncio
from app.config import get_settings
from app.database.connection import execute_query, execute_one
from app.services.video_service import grabar_clip
from app.services.notificacion import (
    Notificador,
    AlertaPayload,
    NotificacionTelegram,
    NotificacionWebSocket,
)

settings = get_settings()

# Notificador (patrón Strategy): centraliza el envío de alertas por todos los
# canales. Agregar un canal nuevo (email, SMS, push) es solo crear otra
# EstrategiaNotificacion y registrarla aquí — sin tocar el motor de alertas.
_notificador = Notificador([
    NotificacionWebSocket(),
    NotificacionTelegram(),
])

# Última vez que se generó alerta para cada cámara
_cooldown: dict = {}
# Segundos a esperar antes de generar otra alerta de la misma cámara
COOLDOWN_SEGUNDOS = 30

# Indica si la cámara aún está en periodo de espera
def _en_cooldown(camara_id: str) -> bool:
    import time
    ultimo = _cooldown.get(camara_id, 0)
    return (time.time() - ultimo) < COOLDOWN_SEGUNDOS

# Marca la cámara como recién alertada
def _registrar_cooldown(camara_id: str):
    import time
    _cooldown[camara_id] = time.time()

# Inserta una alerta en la BD y devuelve su ID
def _guardar_alerta(camara_id: str, tipo_id: int, confianza: float) -> str:
    alerta_id = str(uuid.uuid4())
    execute_query(
        """INSERT INTO alertas (id, camara_id, tipo_id, confianza)
           VALUES (%s, %s, %s, %s)""",
        (alerta_id, camara_id, tipo_id, confianza)
    )
    return alerta_id



# Guarda los metadatos del video asociado a la alerta
def _guardar_video(alerta_id: str, datos_video: dict) -> str:
    video_id = str(uuid.uuid4())
    execute_query(
        """INSERT INTO videos_alerta
           (id, alerta_id, ruta_archivo, duracion_seg, tamano_bytes)
           VALUES (%s, %s, %s, %s, %s)""",
        (
            video_id,
            alerta_id,
            datos_video["ruta_archivo"],
            datos_video["duracion_seg"],
            datos_video["tamano_bytes"]
        )
    )
    return video_id

# Procesa las detecciones de un frame: guarda alerta, graba video, notifica.
# Todo va dentro de un try/except: un error aquí (p. ej. la cámara se eliminó
# justo durante la alerta) NO debe matar el hilo de detección del stream.
def procesar_deteccion(camara_id: str, detecciones: list):
    if not detecciones:
        return
    # Evita generar alertas seguidas de la misma cámara
    if _en_cooldown(camara_id):
        return

    # De todas las detecciones del frame, queda con la de mayor confianza
    mejor = max(detecciones, key=lambda d: d["confianza"])
    clase = mejor["clase"]
    confianza = mejor["confianza"]

    # Traduce la clase del modelo a tipo_id de la BD
    tipo_map = {"fire": 1, "smoke": 2}
    tipo_id = tipo_map.get(clase, 1)

    print(f"Alerta detectada — cámara: {camara_id}, clase: {clase}, confianza: {confianza}")

    _registrar_cooldown(camara_id)

    try:
        # Persiste la alerta en la BD
        alerta_id = _guardar_alerta(camara_id, tipo_id, confianza)
        print(f"Alerta guardada: {alerta_id}")

        # Graba un clip de los últimos segundos (si hay video, va adjunto a Telegram)
        datos_video = grabar_clip(camara_id)
        ruta_video = None
        # Solo guarda el video si la alerta sigue existiendo (la cámara pudo
        # eliminarse durante la grabación, lo que borra la alerta en cascada).
        if datos_video and _alerta_existe(alerta_id):
            video_id = _guardar_video(alerta_id, datos_video)
            ruta_video = datos_video["ruta_archivo"]
            print(f"Video guardado: {video_id}")

        # Obtiene destino de Telegram y ubicación del dueño de la cámara
        info = _info_notificacion(camara_id)

        # Notifica por TODOS los canales vía el patrón Strategy. Cada estrategia
        # decide si puede enviar (WebSocket siempre; Telegram solo si hay chat).
        _notificador.notificar(AlertaPayload(
            alerta_id=alerta_id,
            camara_id=camara_id,
            clase=clase,
            confianza=confianza,
            ubicacion=info.get("ubicacion") if info else None,
            ruta_video=ruta_video,
            chat_id_destino=info.get("telegram_chat_id") if info else None,
        ))
    except Exception as e:
        # No propagar: un fallo procesando una alerta no debe tumbar el stream
        print(f"Error procesando alerta de cámara {camara_id}: {e}")

# Indica si una alerta sigue existiendo en la BD (pudo borrarse en cascada
# si se eliminó la cámara durante el procesamiento)
def _alerta_existe(alerta_id: str) -> bool:
    return execute_one("SELECT id FROM alertas WHERE id = %s", (alerta_id,)) is not None

# Busca el chat_id de Telegram del dueño y la ubicación de la cámara
def _info_notificacion(camara_id: str):
    return execute_one(
        """SELECT u.telegram_chat_id, ub.nombre AS ubicacion
           FROM camaras c
           JOIN usuarios u ON u.id = c.usuario_id
           JOIN ubicaciones ub ON ub.id = c.ubicacion_id
           WHERE c.id = %s""",
        (camara_id,)
    )
