# Cliente MQTT para recibir lecturas de sensores IoT en tiempo real
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from app.config import get_settings
from app.repositories import dispositivo_repo, lectura_repo

settings = get_settings()

# Caché en memoria: última lectura de cada dispositivo para WebSocket
ultimas_lecturas: dict = {}

# Lista de callbacks suscritos a nuevas lecturas MQTT
_suscriptores: list = []


def suscribir(callback):
    # Registrar callback para notificar cuando llegue una nueva lectura
    _suscriptores.append(callback)


def _notificar(lectura: dict):
    # Ejecutar todos los callbacks suscritos
    for callback in _suscriptores:
        try:
            callback(lectura)
        except Exception:
            pass


def _on_connect(client, userdata, flags, rc):
    # Callback: se ejecuta cuando se conecta al broker MQTT
    if rc == 0:
        print(f"MQTT conectado al broker {settings.mqtt_broker}")
        client.subscribe(settings.mqtt_topic)
        print(f"Suscrito al topic: {settings.mqtt_topic}")
    else:
        print(f"Error MQTT al conectar, código: {rc}")


def _on_message(client, userdata, msg):
    # Callback: se ejecuta al recibir un mensaje MQTT
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"MQTT recibido: {payload}")

        dispositivo_id = payload.get("dispositivo_id")
        if not dispositivo_id:
            print("MQTT: payload sin dispositivo_id, ignorando")
            return

        # Validar que el dispositivo exista y esté activo
        dispositivo = dispositivo_repo.obtener_activo_por_id(dispositivo_id)
        if not dispositivo:
            print(f"MQTT: dispositivo {dispositivo_id} no encontrado o inactivo")
            return

        # Guardar lectura en BD y actualizar caché
        lectura_repo.crear(dispositivo_id, payload)

        ultimas_lecturas[dispositivo_id] = {
            "dispositivo_id": dispositivo_id,
            "temperatura": payload.get("temperatura"),
            "humedad": payload.get("humedad"),
            "co2_ppm": payload.get("co2"),
            "registrado_en": datetime.now().isoformat()
        }

        # Notificar a WebSocket para actualizar frontend en tiempo real
        _notificar(ultimas_lecturas[dispositivo_id])

    except json.JSONDecodeError:
        print("MQTT: payload no es JSON válido")
    except Exception as e:
        print(f"MQTT error al procesar mensaje: {e}")


def _on_disconnect(client, userdata, rc):
    # Callback: se ejecuta al desconectarse del broker
    if rc != 0:
        print(f"MQTT desconectado inesperadamente, código: {rc}")


# Cliente MQTT global
_client = None


def iniciar_mqtt():
    # Crear cliente MQTT y conectar a broker en hilo separado
    global _client
    _client = mqtt.Client()
    _client.on_connect = _on_connect
    _client.on_message = _on_message
    _client.on_disconnect = _on_disconnect

    try:
        _client.connect(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
        # loop_start() ejecuta MQTT en hilo secundario sin bloquear FastAPI
        _client.loop_start()
        print("MQTT iniciado en hilo secundario")
    except Exception as e:
        print(f"MQTT no pudo conectar: {e} — continuando sin MQTT")


def detener_mqtt():
    # Detener el loop de MQTT y cerrar conexión
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        print("MQTT detenido")
