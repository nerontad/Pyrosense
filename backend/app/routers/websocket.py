from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.mqtt_client import suscribir, ultimas_lecturas
import asyncio

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.conexiones_sensores: list[WebSocket] = []
        self.conexiones_alertas:  list[WebSocket] = []
        self._loop = None

    def set_loop(self, loop):
        self._loop = loop

    async def conectar_sensores(self, ws: WebSocket):
        await ws.accept()
        self.conexiones_sensores.append(ws)

    async def conectar_alertas(self, ws: WebSocket):
        await ws.accept()
        self.conexiones_alertas.append(ws)

    def desconectar(self, ws: WebSocket):
        if ws in self.conexiones_sensores:
            self.conexiones_sensores.remove(ws)
        if ws in self.conexiones_alertas:
            self.conexiones_alertas.remove(ws)

    async def broadcast_sensores(self, data: dict):
        for ws in self.conexiones_sensores.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    async def broadcast_alertas(self, data: dict):
        for ws in self.conexiones_alertas.copy():
            try:
                await ws.send_json(data)
            except Exception:
                self.desconectar(ws)

    def broadcast_alertas_threadsafe(self, data: dict):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_alertas(data),
                self._loop
            )

    def broadcast_sensores_threadsafe(self, data: dict):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.broadcast_sensores(data),
                self._loop
            )

manager = ConnectionManager()

def _on_lectura_mqtt(lectura: dict):
    manager.broadcast_sensores_threadsafe(lectura)

suscribir(_on_lectura_mqtt)

@router.websocket("/ws/sensores")
async def ws_sensores(websocket: WebSocket):
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
    manager.set_loop(asyncio.get_event_loop())
    await manager.conectar_alertas(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar(websocket)