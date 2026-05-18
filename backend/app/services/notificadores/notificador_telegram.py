import threading
from app.services.notificadores.notificador_base import NotificadorAlerta
from app.repositories import camara_repo


class NotificadorTelegram(NotificadorAlerta):
    """Estrategia: envía la alerta con video por Telegram al dueño de la cámara."""

    def enviar(self, alerta: dict) -> None:
        # Solo envía si hay video adjunto
        datos_video = alerta.get("datos_video")
        if not datos_video:
            return

        threading.Thread(
            target=self._enviar_en_hilo,
            args=(alerta, datos_video),
            daemon=True
        ).start()

    def _enviar_en_hilo(self, alerta: dict, datos_video: dict):
        # Ejecuta en background para no bloquear el motor de alertas
        try:
            from app.services.telegram_service import enviar_alerta_video
            camara = camara_repo.obtener_info_telegram(alerta["camara_id"])
            if camara and camara.get("telegram_chat_id"):
                enviar_alerta_video(
                    chat_id=camara["telegram_chat_id"],
                    ruta_video=datos_video["ruta_archivo"],
                    ubicacion=camara["ubicacion"],
                    clase=alerta["clase"],
                    confianza=alerta["confianza"],
                    alerta_id=alerta["alerta_id"]
                )
            else:
                print("Telegram no configurado para este usuario")
        except Exception as e:
            print(f"Error al enviar Telegram: {e}")
