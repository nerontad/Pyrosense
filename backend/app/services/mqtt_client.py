import json
import paho.mqtt.client as mqtt
from datetime import datetime
from app.config import get_settings
from app.repositories import lectura_repo, dispositivo_repo

settings = get_settings()

# Almacena la última lectura de cada dispositivo en memoria
# para enviarlo por WebSocket sin consultar la BD
ultimas_lecturas: dict = {}

# --- Patrón Observer ---
# Callbacks que se ejecutan cuando llega una lectura nueva.
# El WebSocket se suscribe aquí.
_suscriptores: list = []

def suscribir(callback):
    _suscriptores.append(callback)

def _notificar(lectura: dict):
    for callback in _suscriptores:
        try:
            callback(lectura)
        except Exception:
            pass


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"MQTT conectado al broker {settings.mqtt_broker}")
        client.subscribe(settings.mqtt_topic)
        print(f"Suscrito al topic: {settings.mqtt_topic}")
    else:
        print(f"Error MQTT al conectar, código: {rc}")

def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"MQTT recibido: {payload}")

        dispositivo_id = payload.get("dispositivo_id")
        if not dispositivo_id:
            print("MQTT: payload sin dispositivo_id, ignorando")
            return

        if not dispositivo_repo.existe_activo(dispositivo_id):
            print(f"MQTT: dispositivo {dispositivo_id} no encontrado o inactivo")
            return

        # Persistir lectura vía repositorio
        lectura_repo.crear(
            dispositivo_id=dispositivo_id,
            temperatura=payload.get("temperatura"),
            humedad=payload.get("humedad"),
            co2_ppm=payload.get("co2")
        )

        # Cachear en memoria para WebSocket
        ultimas_lecturas[dispositivo_id] = {
            "dispositivo_id": dispositivo_id,
            "temperatura": payload.get("temperatura"),
            "humedad": payload.get("humedad"),
            "co2_ppm": payload.get("co2"),
            "registrado_en": datetime.now().isoformat()
        }

        # Notificar a observadores (WebSockets)
        _notificar(ultimas_lecturas[dispositivo_id])

    except json.JSONDecodeError:
        print("MQTT: payload no es JSON válido")
    except Exception as e:
        print(f"MQTT error al procesar mensaje: {e}")

def _on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"MQTT desconectado inesperadamente, código: {rc}")

# Cliente MQTT global
_client = None

def iniciar_mqtt():
    global _client
    _client = mqtt.Client()
    _client.on_connect    = _on_connect
    _client.on_message    = _on_message
    _client.on_disconnect = _on_disconnect

    try:
        _client.connect(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
        _client.loop_start()
        print("MQTT iniciado en hilo secundario")
    except Exception as e:
        print(f"MQTT no pudo conectar: {e} — continuando sin MQTT")

def detener_mqtt():
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        print("MQTT detenido")
