from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.mqtt_client import suscribir, ultimas_lecturas
import asyncio

router = APIRouter(tags=["WebSocket"])

# Mantiene las conexiones WebSocket activas y permite enviar datos a todas
class ConnectionManager:
    def __init__(self):
        # Clientes conectados a lecturas de sensores en tiempo real
        self.conexiones_sensores: list[WebSocket] = []
        # Clientes conectados a notificaciones de alertas
        self.conexiones_alertas:  list[WebSocket] = []
        # Event loop guardado para llamadas desde hilos externos
        self._loop = None

    # Guarda el event loop principal
    def set_loop(self, loop):
        self._loop = loop

    # Acepta y registra una conexión al canal de sensores
    async def conectar_sensores(self, ws: WebSocket):
        await ws.accept()
        self.conexiones_sensores.append(ws)

    # Acepta y registra una conexión al canal de alertas
    async def conectar_alertas(self, ws: WebSocket):
        await ws.accept()
        self.conexiones_alertas.append(ws)

    # Quita la conexión de ambos canales
    def desconectar(self, ws: WebSocket):
        if ws in self.conexiones_sensores:
            self.conexiones_sensores.remove(ws)
        if ws in self.conexiones_alertas:
            self.conexiones_alertas.remove(ws)

    # Manda una lectura a todos los clientes de sensores
    async def broadcast_sensores(self, data: dict):
        for ws in self.conexiones_sensores.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    # Manda una alerta a todos los clientes de alertas
    async def broadcast_alertas(self, data: dict):
        for ws in self.conexiones_alertas.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    # Versión segura para llamar desde hilos no-async (MQTT, ffmpeg)
    def broadcast_alertas_threadsafe(self, data: dict):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_alertas(data),
                self._loop
            )

    # Versión segura para llamar desde hilos no-async
    def broadcast_sensores_threadsafe(self, data: dict):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_sensores(data),
                self._loop
            )

# Instancia global del gestor de conexiones
manager = ConnectionManager()

# Callback que reenvía cada lectura MQTT por WebSocket
def _on_lectura_mqtt(lectura: dict):
    manager.broadcast_sensores_threadsafe(lectura)

# Suscribe el callback al cliente MQTT
suscribir(_on_lectura_mqtt)

# Canal WebSocket que envía lecturas de sensores en tiempo real
@router.websocket("/ws/sensores")
async def ws_sensores(websocket: WebSocket):
    manager.set_loop(asyncio.get_event_loop())
    await manager.conectar_sensores(websocket)
    try:
        # Envía las últimas lecturas conocidas al conectar
        if ultimas_lecturas:
            await websocket.send_json({
                "tipo": "lecturas_iniciales",
                "datos": ultimas_lecturas
            })
        # Mantiene la conexión abierta hasta que el cliente se desconecte
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar(websocket)

# Canal WebSocket que notifica nuevas alertas de incendio
@router.websocket("/ws/alertas")
async def ws_alertas(websocket: WebSocket):
    manager.set_loop(asyncio.get_event_loop())
    await manager.conectar_alertas(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar(websocket)
