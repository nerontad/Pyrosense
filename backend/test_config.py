from app.config import get_settings

# Script rápido para verificar que las variables de entorno cargan bien
settings = get_settings()
print("DB:", settings.db_name)
print("Host:", settings.db_host)
print("Secret Key:", settings.secret_key[:10] + "...")
print("Modelo:", settings.model_path)
