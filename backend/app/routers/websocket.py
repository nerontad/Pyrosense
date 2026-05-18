from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.mqtt_client import suscribir, ultimas_lecturas
import asyncio

# Gestor de conexiones WebSocket en tiempo real para sensores y alertas
router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        # Mantiene listas de conexiones WebSocket activas por tipo
        self.conexiones_sensores: list[WebSocket] = []
        self.conexiones_alertas:  list[WebSocket] = []
        self._loop = None

    def set_loop(self, loop):
        # Configura el event loop para operaciones thread-safe
        self._loop = loop

    async def conectar_sensores(self, ws: WebSocket):
        # Acepta una nueva conexión WebSocket de sensores
        await ws.accept()
        self.conexiones_sensores.append(ws)

    async def conectar_alertas(self, ws: WebSocket):
        # Acepta una nueva conexión WebSocket de alertas
        await ws.accept()
        self.conexiones_alertas.append(ws)

    def desconectar(self, ws: WebSocket):
        # Elimina una conexión desconectada de ambas listas
        if ws in self.conexiones_sensores:
            self.conexiones_sensores.remove(ws)
        if ws in self.conexiones_alertas:
            self.conexiones_alertas.remove(ws)

    async def broadcast_sensores(self, data: dict):
        # Envía datos de sensores a todos los clientes conectados
        for ws in self.conexiones_sensores.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    async def broadcast_alertas(self, data: dict):
        # Envía alertas en tiempo real a todos los clientes conectados
        for ws in self.conexiones_alertas.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    def broadcast_alertas_threadsafe(self, data: dict):
        # Envía alertas desde un thread diferente de forma segura
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_alertas(data),
                self._loop
            )

    def broadcast_sensores_threadsafe(self, data: dict):
        # Envía sensores desde un thread diferente de forma segura
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_sensores(data),
                self._loop
            )

manager = ConnectionManager()

def _on_lectura_mqtt(lectura: dict):
    # Callback que distribuye lecturas MQTT a todos los clientes WebSocket
    manager.broadcast_sensores_threadsafe(lectura)

suscribir(_on_lectura_mqtt)

@router.websocket("/ws/sensores")
async def ws_sensores(websocket: WebSocket):
    # Endpoint WebSocket para transmisión en vivo de datos de sensores
    manager.set_loop(asyncio.get_event_loop())
    await manager.conectar_sensores(websocket)
    try:
        if ultimas_lecturas:
            await websocket.send_json({
                "tipo": "lecturas_iniciales",
                "datos": ultimas_lecturas
            })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar(websocket)

@router.websocket("/ws/alertas")
async def ws_alertas(websocket: WebSocket):
    # Endpoint WebSocket para notificaciones de alertas en tiempo real
    manager.set_loop(asyncio.get_event_loop())
    await manager.conectar_alertas(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar(websocket)