import uuid
import asyncio
from app.config import get_settings
from app.database.connection import execute_query, execute_one
from app.services.video_service import grabar_clip

settings = get_settings()

# Cooldown para evitar alertas duplicadas por cámara
_cooldown: dict = {}
COOLDOWN_SEGUNDOS = 30

def _en_cooldown(camara_id: str) -> bool:
    import time
    ultimo = _cooldown.get(camara_id, 0)
    return (time.time() - ultimo) < COOLDOWN_SEGUNDOS

def _registrar_cooldown(camara_id: str):
    import time
    _cooldown[camara_id] = time.time()

def _guardar_alerta(camara_id: str, tipo_id: int, confianza: float) -> str:
    alerta_id = str(uuid.uuid4())
    execute_query(
        """INSERT INTO alertas (id, camara_id, tipo_id, confianza)
           VALUES (%s, %s, %s, %s)""",
        (alerta_id, camara_id, tipo_id, confianza)
    )
    return alerta_id



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

def procesar_deteccion(camara_id: str, detecciones: list):
    if not detecciones:
        return
    if _en_cooldown(camara_id):
        return

    # Tomar la detección con mayor confianza
    mejor = max(detecciones, key=lambda d: d["confianza"])
    clase = mejor["clase"]
    confianza = mejor["confianza"]

    # Mapear clase a tipo_alerta
    tipo_map = {"fire": 1, "smoke": 2}
    tipo_id = tipo_map.get(clase, 1)

    print(f"Alerta detectada — cámara: {camara_id}, clase: {clase}, confianza: {confianza}")

    _registrar_cooldown(camara_id)

  # Guardar alerta en BD
    alerta_id = _guardar_alerta(camara_id, tipo_id, confianza)
    print(f"Alerta guardada: {alerta_id}")

    # Notificar por WebSocket
    notificar_alerta_ws(alerta_id, camara_id, clase, confianza)

    

    # Grabar clip de video
    datos_video = grabar_clip(camara_id)
    if datos_video:
        video_id = _guardar_video(alerta_id, datos_video)
        print(f"Video guardado: {video_id}")

        # Enviar por Telegram en hilo separado
        import threading
        threading.Thread(
            target=_enviar_telegram,
            args=(alerta_id, datos_video, camara_id, clase, confianza),
            daemon=True
        ).start()

def _enviar_telegram(alerta_id: str, datos_video: dict, camara_id: str, clase: str, confianza: float):
    try:
        from app.services.telegram_service import enviar_alerta_video
        # Obtener chat_id del usuario dueño de la cámara
        camara = execute_one(
            """SELECT u.telegram_chat_id, ub.nombre as ubicacion
               FROM camaras c
               JOIN usuarios u ON u.id = c.usuario_id
               JOIN ubicaciones ub ON ub.id = c.ubicacion_id
               WHERE c.id = %s""",
            (camara_id,)
        )
        if camara and camara.get("telegram_chat_id"):
            enviar_alerta_video(
                chat_id=camara["telegram_chat_id"],
                ruta_video=datos_video["ruta_archivo"],
                ubicacion=camara["ubicacion"],
                clase=clase,
                confianza=confianza,
                alerta_id=alerta_id
            )
        else:
            print("Telegram no configurado para este usuario")
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")

def notificar_alerta_ws(alerta_id: str, camara_id: str, clase: str, confianza: float):
    try:
        from app.routers.websocket import manager
        data = {
            "tipo": "nueva_alerta",
            "alerta_id": alerta_id,
            "camara_id": camara_id,
            "clase": clase,
            "confianza": confianza
        }
        manager.broadcast_alertas_threadsafe(data)
    except Exception as e:
        print(f"Error notificando alerta por WS: {e}")