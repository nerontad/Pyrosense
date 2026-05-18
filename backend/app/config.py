# Configuración de la aplicación desde variables de entorno
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Configuración de base de datos PostgreSQL
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # Configuración de autenticación con JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Configuración MQTT para comunicación IoT
    mqtt_broker: str
    mqtt_port: int
    mqtt_topic: str

    # Token para notificaciones por Telegram
    telegram_token: str

    # Configuración del modelo de IA (ONNX)
    model_path: str
    confidence_threshold: float
    model_drive_id: str

    # Configuración de grabación de videos
    video_output_dir: str
    buffer_seconds: int

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "protected_namespaces": ()}

# Singleton: retorna la misma instancia de Settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()