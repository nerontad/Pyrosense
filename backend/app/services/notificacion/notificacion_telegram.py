import threading
from app.services.notificacion.base import EstrategiaNotificacion, AlertaPayload


class NotificacionTelegram(EstrategiaNotificacion):
    """Envía la alerta por Telegram al chat del dueño de la cámara.

    Se ejecuta en un hilo aparte para no bloquear el pipeline de detección.
    Requiere chat_id_destino y ruta_video en el payload.
    """

    def nombre(self) -> str:
        return "telegram"

    def puede_enviar(self, payload: AlertaPayload) -> bool:
        return bool(payload.chat_id_destino) and bool(payload.ruta_video)

    def enviar(self, payload: AlertaPayload) -> None:
        threading.Thread(
            target=self._enviar_sync,
            args=(payload,),
            daemon=True
        ).start()

    def _enviar_sync(self, payload: AlertaPayload) -> None:
        try:
            from app.services.telegram_service import enviar_alerta_video
            enviar_alerta_video(
                chat_id=payload.chat_id_destino,
                ruta_video=payload.ruta_video,
                ubicacion=payload.ubicacion or "Ubicación desconocida",
                clase=payload.clase,
                confianza=payload.confianza,
                alerta_id=payload.alerta_id,
            )
        except Exception as e:
            print(f"NotificacionTelegram: error — {e}")
