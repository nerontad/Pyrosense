import asyncio
import concurrent.futures
from telegram import Bot
from telegram.error import TelegramError
from app.config import get_settings
from app.database.connection import execute_query

settings = get_settings()


# Registra la URL del webhook en el bot de Telegram
async def configurar_webhook(base_url: str):
    try:
        bot = Bot(token=settings.telegram_token)
        webhook_url = f"{base_url}/telegram/webhook"
        await bot.set_webhook(webhook_url)
        print(f"Webhook configurado: {webhook_url}")
    except Exception as e:
        print(f"Error configurando webhook: {e}")

# Sube el video al chat indicado y marca la alerta como enviada
async def _enviar_video_async(chat_id: str, ruta_video: str, caption: str, alerta_id: str):
    try:
        bot = Bot(token=settings.telegram_token)
        with open(ruta_video, "rb") as video:
            await bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=caption,
                supports_streaming=True
            )
        # Marca el video como enviado por Telegram en la BD
        execute_query(
            "UPDATE videos_alerta SET enviado_telegram = 1 WHERE alerta_id = %s",
            (alerta_id,)
        )
        print(f"Telegram: video enviado a {chat_id}")
    except TelegramError as e:
        print(f"Telegram error: {e}")
    except FileNotFoundError:
        print(f"Telegram: archivo no encontrado {ruta_video}")
    except Exception as e:
        print(f"Telegram error inesperado: {e}")

# Construye el caption y dispara el envío del video por Telegram
def enviar_alerta_video(
    chat_id: str,
    ruta_video: str,
    ubicacion: str,
    clase: str,
    confianza: float,
    alerta_id: str
):
    # Emoji y texto del mensaje de alerta
    emoji = "🔥" if clase == "fire" else "💨"
    caption = (
        f"{emoji} Alerta de incendio detectada\n"
        f"📍 Ubicación: {ubicacion}\n"
        f"🔍 Tipo: {clase}\n"
        f"📊 Confianza: {confianza:.0%}"
    )
    try:
        # Ejecuta la corutina en un nuevo event loop (funciona desde cualquier hilo)
        asyncio.run(
            _enviar_video_async(chat_id, ruta_video, caption, alerta_id)
        )
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")
