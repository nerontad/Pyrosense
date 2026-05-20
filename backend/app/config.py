from pydantic_settings import BaseSettings
from functools import lru_cache

# Configuración global de la app cargada desde variables de entorno o .env
class Settings(BaseSettings):
    # Conexión MySQL
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # Firma de tokens JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Broker MQTT para sensores IoT
    mqtt_broker: str
    mqtt_port: int
    mqtt_topic: str

    # Bot de Telegram para alertas
    telegram_token: str

    # Modelo IA de detección
    model_path: str
    confidence_threshold: float

    # Salida de videos grabados al detectar
    video_output_dir: str
    buffer_seconds: int

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "protected_namespaces": ()}

# Devuelve la instancia cacheada de Settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()
