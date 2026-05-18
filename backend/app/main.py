# Aplicación principal de FastAPI con configuración de CORS, routers y ciclo de vida
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import auth, usuario, dispositivo, camara, lectura, alerta, websocket, ubicacion, tipos, telegram
from app.services.mqtt_client import iniciar_mqtt, detener_mqtt
from app.services.vision_service import vision
from app.services.stream_service import iniciar_stream, detener_todos
from app.repositories import camara_repo
import os

settings = get_settings()

# Ejecutar al iniciar y cerrar la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando sistema detector de incendios...")
    # Conectar broker MQTT
    iniciar_mqtt()
    print(f"Modelo cargado: {vision.modelo_cargado()}")

    # Iniciar streaming de video en todas las cámaras activas
    camaras = camara_repo.listar_activas()
    for cam in camaras:
        print(f"Iniciando detección automática: {cam['nombre']}")
        iniciar_stream(cam["id"], cam["url_rtsp"])

    yield
    # Cerrar conexiones al apagar
    detener_todos()
    detener_mqtt()
    print("Cerrando sistema...")

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema Detector de Incendios",
    description="API REST para detección de incendios con IA e IoT",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir solicitudes del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de todas las secciones
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(dispositivo.router)
app.include_router(camara.router)
app.include_router(lectura.router)
app.include_router(alerta.router)
app.include_router(websocket.router)
app.include_router(ubicacion.router)
app.include_router(tipos.router)
app.include_router(telegram.router)

# Crear directorio de videos y servir como archivos estáticos
os.makedirs("videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# CORS para desarrollo y producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://detector-incendios.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz
@app.get("/")
def root():
    return {"mensaje": "Sistema detector de incendios activo"}

# Endpoint de salud para verificar estado del servidor y modelo
@app.get("/health")
def health():
    return {
        "estado": "ok",
        "version": "1.0.0",
        "modelo_cargado": vision.modelo_cargado()
    }

