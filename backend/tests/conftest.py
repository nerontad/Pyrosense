import os
import sys
import pytest

# Permite importar `app.*` ejecutando pytest desde la carpeta backend/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Variables mínimas de entorno para que `Settings` cargue sin .env real.
# Los tests no tocan BD/MQTT reales, así que basta con que la validación pase.
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("MQTT_BROKER", "localhost")
os.environ.setdefault("MQTT_PORT", "1883")
os.environ.setdefault("MQTT_TOPIC", "sensores/test")
os.environ.setdefault("TELEGRAM_TOKEN", "test-token")
os.environ.setdefault("MODEL_PATH", "/tmp/model.onnx")
os.environ.setdefault("CONFIDENCE_THRESHOLD", "0.5")
os.environ.setdefault("VIDEO_OUTPUT_DIR", "/tmp/videos")
os.environ.setdefault("BUFFER_SECONDS", "10")


@pytest.fixture
def fake_execute(monkeypatch):
    """Reemplaza execute_query / execute_one por una versión que registra
    las llamadas, así los tests pueden inspeccionar qué SQL se intentó
    ejecutar sin tocar MySQL."""
    llamadas = {"query": [], "one": []}

    def _execute_query(sql, params=None, fetch=False):
        llamadas["query"].append((sql, params, fetch))
        return [] if fetch else 1

    def _execute_one(sql, params=None):
        llamadas["one"].append((sql, params))
        return None

    from app.database import connection as conn_mod
    monkeypatch.setattr(conn_mod, "execute_query", _execute_query)
    monkeypatch.setattr(conn_mod, "execute_one", _execute_one)
    return llamadas
