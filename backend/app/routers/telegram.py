from fastapi import APIRouter, Request
from app.config import get_settings
from app.repositories import usuario_repo

settings = get_settings()
# Webhook para recibir mensajes de Telegram y registrar notificaciones
router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/webhook")
async def webhook(request: Request):
    # Procesa mensajes de Telegram para vincular chat_id con cuenta de usuario
    data = await request.json()
    try:
        message = data.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        texto = message.get("text", "")

        if not chat_id:
            return {"ok": True}

        if texto == "/start":
            usuario = usuario_repo.obtener_por_telegram_chat_id(chat_id)
            if usuario:
                await _responder(chat_id,
                    f"✅ Hola {usuario['nombre']}, ya estás registrado.\n"
                    f"Recibirás alertas de incendio automáticamente.")
            else:
                await _responder(chat_id,
                    f"👋 Bienvenido al bot de alertas de incendios.\n\n"
                    f"Tu Chat ID es: <code>{chat_id}</code>\n\n"
                    f"Copia este número y pégalo en la sección "
                    f"<b>Mi perfil → Notificaciones Telegram</b> "
                    f"de la aplicación web para activar las alertas.")
    except Exception as e:
        print(f"Error en webhook Telegram: {e}")

    return {"ok": True}


async def _responder(chat_id: str, texto: str):
    # Envía un mensaje de respuesta al usuario en Telegram
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML"
            }
        )
