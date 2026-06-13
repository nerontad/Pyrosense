import threading
from app.services.notificacion.base import EstrategiaNotificacion, AlertaPayload


class NotificacionTelegram(EstrategiaNotificacion):
    """Envía la alerta por Telegram al chat del dueño del origen.

    Se ejecuta en un hilo aparte para no bloquear el pipeline de detección.
    Si el payload trae video (alerta de cámara) envía el clip; si no
    (alerta de sensor) envía un mensaje de solo texto. Solo requiere
    chat_id_destino para poder enviar.
    """

    def nombre(self) -> str:
        return "telegram"

    def puede_enviar(self, payload: AlertaPayload) -> bool:
        return bool(payload.chat_id_destino)

    def enviar(self, payload: AlertaPayload) -> None:
        threading.Thread(
            target=self._enviar_sync,
            args=(payload,),
            daemon=True
        ).start()

    def _enviar_sync(self, payload: AlertaPayload) -> None:
        try:
            ubicacion = payload.ubicacion or "Ubicación desconocida"
            if payload.ruta_video:
                # Alerta de cámara: envía el clip de video
                from app.services.telegram_service import enviar_alerta_video
                enviar_alerta_video(
                    chat_id=payload.chat_id_destino,
                    ruta_video=payload.ruta_video,
                    ubicacion=ubicacion,
                    clase=payload.clase,
                    confianza=payload.confianza,
                    alerta_id=payload.alerta_id,
                )
            else:
                # Alerta de sensor: mensaje de solo texto
                from app.services.telegram_service import enviar_alerta_texto
                enviar_alerta_texto(
                    chat_id=payload.chat_id_destino,
                    ubicacion=ubicacion,
                    motivo=payload.clase,
                )
        except Exception as e:
            print(f"NotificacionTelegram: error — {e}")
