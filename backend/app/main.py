from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import auth, usuario, dispositivo, camara, lectura, alerta, websocket, telegram, tipos
from app.services.mqtt_client import iniciar_mqtt, detener_mqtt
from app.services.vision_service import vision
from app.services.stream_service import detener_todos


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando sistema detector de incendios...")
    iniciar_mqtt()
    print(f"Modelo cargado: {vision.modelo_cargado()}")
    yield
    detener_mqtt()
    print("Cerrando sistema...")

app = FastAPI(
    title="Sistema Detector de Incendios",
    description="API REST para detección de incendios con IA e IoT",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(dispositivo.router)
app.include_router(camara.router)
app.include_router(lectura.router)
app.include_router(alerta.router)
app.include_router(websocket.router)
app.include_router(telegram.router)
app.include_router(tipos.router)

@app.get("/")
def root():
    return {"mensaje": "Sistema detector de incendios activo"}

@app.get("/health")
def health():
    return {
        "estado": "ok",
        "version": "1.0.0",
        "modelo_cargado": vision.modelo_cargado()
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando sistema detector de incendios...")
    iniciar_mqtt()
    print(f"Modelo cargado: {vision.modelo_cargado()}")
    yield
    detener_todos()
    detener_mqtt()
    print("Cerrando sistema...")