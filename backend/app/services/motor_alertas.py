# Motor de alertas: procesa detecciones, crea alertas y notifica por múltiples canales
import time
from app.config import get_settings
from app.repositories import alerta_repo, video_alerta_repo
from app.services.video_service import grabar_clip
from app.services.notificadores import notificadores

settings = get_settings()

# Caché para evitar alertas duplicadas por la misma cámara
_cooldown: dict = {}
COOLDOWN_SEGUNDOS = 30


def _en_cooldown(camara_id: str) -> bool:
    # Verificar si la cámara está en período de espera (cooldown)
    ultimo = _cooldown.get(camara_id, 0)
    return (time.time() - ultimo) < COOLDOWN_SEGUNDOS


def _registrar_cooldown(camara_id: str):
    # Registrar timestamp actual para iniciar cooldown
    _cooldown[camara_id] = time.time()


def procesar_deteccion(camara_id: str, detecciones: list):
    # Procesar detecciones del modelo: crear alerta, grabar video y notificar
    if not detecciones:
        return
    # Ignorar si está en cooldown (para evitar alertas spam)
    if _en_cooldown(camara_id):
        return

    # Seleccionar detección con mayor confianza
    mejor = max(detecciones, key=lambda d: d["confianza"])
    clase = mejor["clase"]
    confianza = mejor["confianza"]

    # Mapear clase a tipo_id para base de datos
    tipo_map = {"fire": 1, "smoke": 2}
    tipo_id = tipo_map.get(clase, 1)

    print(f"Alerta detectada — cámara: {camara_id}, clase: {clase}, confianza: {confianza}")

    _registrar_cooldown(camara_id)

    # Guardar alerta en BD
    alerta_id = alerta_repo.crear(camara_id, tipo_id, confianza)
    print(f"Alerta guardada: {alerta_id}")

    # Grabar video del evento
    datos_video = grabar_clip(camara_id)
    if datos_video:
        video_id = video_alerta_repo.crear(alerta_id, datos_video)
        print(f"Video guardado: {video_id}")

    # Patrón Strategy: notificar por todos los canales sin acoplar servicios
    # Agregar nuevo canal solo requiere extender la lista de notificadores
    payload = {
        "alerta_id": alerta_id,
        "camara_id": camara_id,
        "clase": clase,
        "confianza": confianza,
        "datos_video": datos_video,
    }
    for notificador in notificadores:
        notificador.enviar(payload)
