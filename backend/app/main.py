from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import get_settings
from app.routers import auth, usuario, dispositivo, camara, lectura, alerta, websocket, ubicacion, tipos, telegram
from app.routers import vision as vision_router
from app.services.mqtt_client import iniciar_mqtt, detener_mqtt
from app.services.vision_service import vision
from app.services.stream_service import iniciar_stream, detener_todos
from app.services.limpieza_service import iniciar_limpieza, detener_limpieza
from app.services.telegram_service import configurar_webhook
from app.database.connection import execute_query
from app.middleware.security import SecurityHeadersMiddleware
import os
settings = get_settings()


# Arranque y cierre de la app: MQTT, modelo IA y streams de cámaras.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando sistema detector de incendios...")
    iniciar_mqtt()
    iniciar_limpieza()
    print(f"Modelo cargado: {vision.modelo_cargado()}")

    # Lanza un stream por cada cámara activa registrada en BD
    camaras = execute_query(
        "SELECT id, url_rtsp, nombre FROM camaras WHERE activo = 1",
        fetch=True
    )
    
    from app.utils.crypto_rtsp import descifrar_url
    for cam in camaras:
        print(f"Iniciando detección automática: {cam['nombre']}")
        iniciar_stream(cam["id"], descifrar_url(cam["url_rtsp"]))

    # Registra el webhook de Telegram para que el bot reciba mensajes (/start, etc.)
    # Usa WEBHOOK_BASE_URL si está definido; si no, el dominio público de Railway.
    base_url = os.getenv("WEBHOOK_BASE_URL")
    if not base_url and os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        base_url = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}"
    if base_url:
        await configurar_webhook(base_url)
    else:
        print("WEBHOOK_BASE_URL/RAILWAY_PUBLIC_DOMAIN no definidos — webhook de Telegram NO registrado")

    yield
    # Detiene streams, MQTT y job de limpieza al cerrar el proceso
    detener_todos()
    detener_mqtt()
    detener_limpieza()
    print("Cerrando sistema...")

app = FastAPI(
    title="Sistema Detector de Incendios",
    description="API REST para detección de incendios con IA e IoT",
    version="1.0.0",
    lifespan=lifespan,
)

# Añade cabeceras de seguridad a cada respuesta HTTP
app.add_middleware(SecurityHeadersMiddleware)

# Orígenes que pueden hacer peticiones cross-origin a la API
ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://pyrosense.vercel.app",
    "https://proyecto-de-titulo-pearl.vercel.app",
]

# CORS con métodos y headers concretos (no wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    expose_headers=[],
    max_age=600,
)

# Registro de routers de la API
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
app.include_router(vision_router.router)

# Sirve los videos generados por las detecciones
os.makedirs("videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")


@app.get("/")
def root():
    return {"mensaje": "Sistema detector de incendios activo"}

# Endpoint de healthcheck (estado del servicio y modelo IA)
@app.get("/health")
def health():
    return {
        "estado": "ok",
        "version": "1.0.0",
        "modelo_cargado": vision.modelo_cargado()
    }
