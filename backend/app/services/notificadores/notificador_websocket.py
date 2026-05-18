from app.services.notificadores.notificador_base import NotificadorAlerta


class NotificadorWebSocket(NotificadorAlerta):
    """Estrategia: notifica la alerta a los clientes WebSocket conectados."""

    def enviar(self, alerta: dict) -> None:
        # Broadcast en tiempo real a frontend via WebSocket
        try:
            from app.routers.websocket import manager
            data = {
                "tipo": "nueva_alerta",
                "alerta_id": alerta["alerta_id"],
                "camara_id": alerta["camara_id"],
                "clase": alerta["clase"],
                "confianza": alerta["confianza"],
            }
            manager.broadcast_alertas_threadsafe(data)
        except Exception as e:
            print(f"Error notificando alerta por WS: {e}")
