import asyncio
import concurrent.futures
from telegram import Bot
from telegram.error import TelegramError
from app.config import get_settings
from app.database.connection import execute_query

settings = get_settings()

# Número máximo de intentos antes de abandonar
MAX_REINTENTOS = 3
# Espera base en segundos entre reintentos (backoff exponencial: 5s → 10s → 20s)
ESPERA_BASE_S = 5


# Registra la URL del webhook en el bot de Telegram
async def configurar_webhook(base_url: str):
    try:
        bot = Bot(token=settings.telegram_token)
        webhook_url = f"{base_url}/telegram/webhook"
        await bot.set_webhook(webhook_url)
        print(f"Webhook configurado: {webhook_url}")
    except Exception as e:
        print(f"Error configurando webhook: {e}")

# Sube el video al chat indicado con reintentos automáticos ante fallos de red.
# En cada fallo de conectividad espera ESPERA_BASE_S * 2^(intento-1) segundos
# antes del siguiente intento (backoff exponencial).
async def _enviar_video_async(chat_id: str, ruta_video: str, caption: str, alerta_id: str):
    bot = Bot(token=settings.telegram_token)

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            with open(ruta_video, "rb") as video:
                await bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    caption=caption,
                    supports_streaming=True
                )
            # Éxito: marca el video como enviado en la BD y termina
            execute_query(
                "UPDATE videos_alerta SET enviado_telegram = 1 WHERE alerta_id = %s",
                (alerta_id,)
            )
            print(f"Telegram: video enviado a {chat_id} (intento {intento}/{MAX_REINTENTOS})")
            return

        except FileNotFoundError:
            # El archivo no existe — no es un problema de red, no tiene sentido reintentar
            print(f"Telegram: archivo no encontrado '{ruta_video}' — sin reintentos")
            return

        except (TelegramError, OSError) as e:
            # Error de conectividad o API de Telegram
            if intento < MAX_REINTENTOS:
                espera = ESPERA_BASE_S * (2 ** (intento - 1))
                print(
                    f"Telegram: intento {intento}/{MAX_REINTENTOS} falló ({e}). "
                    f"Reintentando en {espera}s..."
                )
                await asyncio.sleep(espera)
            else:
                print(
                    f"Telegram: todos los reintentos agotados tras {MAX_REINTENTOS} intentos. "
                    f"Último error: {e}"
                )

        except Exception as e:
            # Error no esperado — no reintentar
            print(f"Telegram error inesperado: {e}")
            return


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


# Envía una alerta de solo texto (p. ej. sensores IoT, que no graban video)
async def _enviar_texto_async(chat_id: str, texto: str):
    bot = Bot(token=settings.telegram_token)
    await bot.send_message(chat_id=chat_id, text=texto)


# Construye el mensaje y lo envía por Telegram sin video adjunto
def enviar_alerta_texto(chat_id: str, ubicacion: str, motivo: str):
    texto = (
        f"⚠️ Alerta de sensor\n"
        f"📍 Ubicación: {ubicacion}\n"
        f"🔍 Motivo: {motivo}"
    )
    try:
        asyncio.run(_enviar_texto_async(chat_id, texto))
    except Exception as e:
        print(f"Error al enviar Telegram (texto): {e}")
