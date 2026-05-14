from app.services.notificacion.base import EstrategiaNotificacion, AlertaPayload


class NotificacionWebSocket(EstrategiaNotificacion):
    """Notifica al frontend conectado por WebSocket."""

    def nombre(self) -> str:
        return "websocket"

    def puede_enviar(self, payload: AlertaPayload) -> bool:
        return True

    def enviar(self, payload: AlertaPayload) -> None:
        try:
            from app.routers.websocket import manager
            manager.broadcast_alertas_threadsafe({
                "tipo": "nueva_alerta",
                "alerta_id": payload.alerta_id,
                "camara_id": payload.camara_id,
                "clase": payload.clase,
                "confianza": payload.confianza,
            })
        except Exception as e:
            print(f"NotificacionWebSocket: error al notificar — {e}")
