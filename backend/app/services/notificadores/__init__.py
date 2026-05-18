"""Patrón Strategy aplicado a la notificación de alertas.

Para agregar un canal nuevo (Slack, email, FCM, ...) basta con crear una
clase que herede de `NotificadorAlerta`, implementar `enviar(alerta)`, e
incluirla en la lista `notificadores`. El motor de alertas no cambia.
"""
from app.services.notificadores.notificador_base import NotificadorAlerta
from app.services.notificadores.notificador_websocket import NotificadorWebSocket
from app.services.notificadores.notificador_telegram import NotificadorTelegram

# Lista de notificadores activos: WebSocket en tiempo real + Telegram
notificadores: list[NotificadorAlerta] = [
    NotificadorWebSocket(),
    NotificadorTelegram(),
]
