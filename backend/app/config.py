from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Base de datos
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # MQTT
    mqtt_broker: str
    mqtt_port: int
    mqtt_topic: str

    # Telegram
    telegram_token: str

    # Modelo ONNX
    model_path: str
    confidence_threshold: float

    # Video
    video_output_dir: str
    buffer_seconds: int

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "protected_namespaces": ()}

@lru_cache()
def get_settings() -> Settings:
    return Settings()