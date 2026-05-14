import time
from app.config import get_settings
from app.repositories import alerta_repo, video_repo, camara_repo
from app.services.video_service import grabar_clip
from app.services.notificacion import (
    Notificador,
    NotificacionTelegram,
    NotificacionWebSocket,
    AlertaPayload,
)

settings = get_settings()

# Cooldown para evitar alertas duplicadas por cámara
_cooldown: dict = {}
COOLDOWN_SEGUNDOS = 30

# Patrón Strategy: el notificador despacha cada alerta por todos los
# canales registrados. Para agregar email/SMS/push solo hay que crear
# otra EstrategiaNotificacion y llamarle a `registrar()`.
notificador = Notificador([
    NotificacionWebSocket(),
    NotificacionTelegram(),
])


def _en_cooldown(camara_id: str) -> bool:
    ultimo = _cooldown.get(camara_id, 0)
    return (time.time() - ultimo) < COOLDOWN_SEGUNDOS

def _registrar_cooldown(camara_id: str):
    _cooldown[camara_id] = time.time()


def procesar_deteccion(camara_id: str, detecciones: list):
    if not detecciones or _en_cooldown(camara_id):
        return

    # Tomar la detección con mayor confianza
    mejor = max(detecciones, key=lambda d: d["confianza"])
    clase = mejor["clase"]
    confianza = mejor["confianza"]

    tipo_map = {"fire": 1, "smoke": 2}
    tipo_id = tipo_map.get(clase, 1)

    print(f"Alerta detectada — cámara: {camara_id}, clase: {clase}, confianza: {confianza}")
    _registrar_cooldown(camara_id)

    # Persistir alerta
    alerta_id = alerta_repo.crear(camara_id, tipo_id, confianza)
    print(f"Alerta guardada: {alerta_id}")

    # Grabar clip de video (si hay buffer disponible)
    datos_video = grabar_clip(camara_id)
    ruta_video = None
    if datos_video:
        video_repo.crear(
            alerta_id=alerta_id,
            ruta_archivo=datos_video["ruta_archivo"],
            duracion_seg=datos_video["duracion_seg"],
            tamano_bytes=datos_video["tamano_bytes"],
        )
        ruta_video = datos_video["ruta_archivo"]

    # Obtener destinatario de Telegram + ubicación
    destino = camara_repo.obtener_con_destinatario_telegram(camara_id) or {}

    payload = AlertaPayload(
        alerta_id=alerta_id,
        camara_id=camara_id,
        clase=clase,
        confianza=confianza,
        ubicacion=destino.get("ubicacion"),
        ruta_video=ruta_video,
        chat_id_destino=destino.get("telegram_chat_id"),
    )

    # Despachar por todos los canales registrados (Strategy)
    notificador.notificar(payload)
