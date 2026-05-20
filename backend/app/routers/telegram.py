from fastapi import APIRouter, Request
from app.database.connection import execute_query, execute_one
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/telegram", tags=["Telegram"])

# Recibe los mensajes del bot de Telegram
@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        message = data.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        texto   = message.get("text", "")
        email   = None

        if not chat_id:
            return {"ok": True}

        # Comando /start: vincula o saluda al usuario
        if texto == "/start":
            usuario = execute_one(
                "SELECT id, nombre FROM usuarios WHERE telegram_chat_id = %s",
                (chat_id,)
            )
            if usuario:
                # Usuario ya vinculado
                await _responder(chat_id,
                    f"✅ Hola {usuario['nombre']}, ya estás registrado.\n"
                    f"Recibirás alertas de incendio automáticamente.")
            else:
                # Devuelve el chat_id para que el usuario lo pegue en la web
                await _responder(chat_id,
                    f"👋 Bienvenido al bot de alertas de incendios.\n\n"
                    f"Tu Chat ID es: <code>{chat_id}</code>\n\n"
                    f"Copia este número y pégalo en la sección "
                    f"<b>Mi perfil → Notificaciones Telegram</b> "
                    f"de la aplicación web para activar las alertas.")
    except Exception as e:
        print(f"Error en webhook Telegram: {e}")

    return {"ok": True}

# Envía un mensaje al chat de Telegram
async def _responder(chat_id: str, texto: str):
    import httpx
    from app.config import get_settings
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML"
            }
        )
