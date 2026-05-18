# Servicio de Telegram: enviar alertas de incendio con videos a usuarios
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from app.config import get_settings
from app.repositories import video_alerta_repo

settings = get_settings()


async def configurar_webhook(base_url: str):
    # Configurar webhook para recibir mensajes de Telegram
    try:
        bot = Bot(token=settings.telegram_token)
        webhook_url = f"{base_url}/telegram/webhook"
        await bot.set_webhook(webhook_url)
        print(f"Webhook configurado: {webhook_url}")
    except Exception as e:
        print(f"Error configurando webhook: {e}")


async def _enviar_video_async(chat_id: str, ruta_video: str, caption: str, alerta_id: str):
    # Enviar video del incendio a Telegram de forma asíncrona
    try:
        bot = Bot(token=settings.telegram_token)
        with open(ruta_video, "rb") as video:
            await bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=caption,
                supports_streaming=True
            )
        # Marcar el video como enviado en la BD
        video_alerta_repo.marcar_enviado_telegram(alerta_id)
        print(f"Telegram: video enviado a {chat_id}")
    except TelegramError as e:
        print(f"Telegram error: {e}")
    except FileNotFoundError:
        print(f"Telegram: archivo no encontrado {ruta_video}")
    except Exception as e:
        print(f"Telegram error inesperado: {e}")


def enviar_alerta_video(
    chat_id: str,
    ruta_video: str,
    ubicacion: str,
    clase: str,
    confianza: float,
    alerta_id: str
):
    # Preparar y enviar alerta de incendio con video
    emoji = "🔥" if clase == "fire" else "💨"
    caption = (
        f"{emoji} Alerta de incendio detectada\n"
        f"📍 Ubicación: {ubicacion}\n"
        f"🔍 Tipo: {clase}\n"
        f"📊 Confianza: {confianza:.0%}"
    )
    try:
        # asyncio.run() crea su propio event loop para no bloquear la app
        asyncio.run(
            _enviar_video_async(chat_id, ruta_video, caption, alerta_id)
        )
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")
