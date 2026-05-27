import json
import uuid
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from app.config import get_settings
from app.database.connection import execute_query, execute_one

settings = get_settings()

# Última lectura conocida de cada dispositivo (cache en memoria)
ultimas_lecturas: dict = {}

# Lista de callbacks que se llaman cuando llega una lectura nueva
_suscriptores: list = []

# Registra una función que será notificada con cada lectura
def suscribir(callback):
    _suscriptores.append(callback)

# Ejecuta todos los callbacks registrados con la nueva lectura
def _notificar(lectura: dict):
    for callback in _suscriptores:
        try:
            callback(lectura)
        except Exception:
            pass

# Inserta una lectura del sensor en la BD y la devuelve
def _guardar_lectura(dispositivo_id: str, datos: dict):
    lectura_id = str(uuid.uuid4())
    # Se almacena en UTC para que el frontend lo convierta a la zona local
    registrado_en = datetime.now(timezone.utc).replace(tzinfo=None)
    # Acepta `co2` (nombre nuevo) o `gas` (firmware antiguo)
    co2 = datos.get("co2")
    if co2 is None:
        co2 = datos.get("gas")
    execute_query(
        """INSERT INTO lecturas_sensores
           (id, dispositivo_id, temperatura, humedad, co2_ppm, registrado_en)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            lectura_id,
            dispositivo_id,
            datos.get("temperatura"),
            datos.get("humedad"),
            co2,
            registrado_en,
        )
    )
    return {
        "id": lectura_id,
        "dispositivo_id": dispositivo_id,
        "temperatura": datos.get("temperatura"),
        "humedad": datos.get("humedad"),
        "co2_ppm": co2,
        "registrado_en": registrado_en,
    }

# Callback cuando se conecta al broker MQTT
def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"MQTT conectado al broker {settings.mqtt_broker}")
        client.subscribe(settings.mqtt_topic)
        print(f"Suscrito al topic: {settings.mqtt_topic}")
    else:
        print(f"Error MQTT al conectar, código: {rc}")

# Callback cuando llega un mensaje MQTT con una lectura
def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"MQTT recibido: {payload}")

        dispositivo_id = payload.get("dispositivo_id")
        if not dispositivo_id:
            print("MQTT: payload sin dispositivo_id, ignorando")
            return

        # Verifica que el dispositivo exista y esté activo
        dispositivo = execute_one(
            "SELECT id FROM dispositivos_iot WHERE id = %s AND activo = 1",
            (dispositivo_id,)
        )
        print(f"MQTT: dispositivo encontrado: {dispositivo}")
        if not dispositivo:
            print(f"MQTT: dispositivo {dispositivo_id} no encontrado o inactivo")
            return

        # Persiste la lectura en MySQL
        lectura = _guardar_lectura(dispositivo_id, payload)
        print(f"MQTT: lectura guardada: {lectura}")

        # Actualiza la cache en memoria para el WebSocket (con la misma marca UTC)
        ultimas_lecturas[dispositivo_id] = {
            "dispositivo_id": dispositivo_id,
            "temperatura": lectura["temperatura"],
            "humedad": lectura["humedad"],
            "co2_ppm": lectura["co2_ppm"],
            "registrado_en": lectura["registrado_en"].replace(tzinfo=timezone.utc).isoformat()
        }

        # Avisa a los suscriptores (WebSocket reenviará al frontend)
        _notificar(ultimas_lecturas[dispositivo_id])

    except json.JSONDecodeError:
        print("MQTT: payload no es JSON válido")
    except Exception as e:
        print(f"MQTT error al procesar mensaje: {e}")
        import traceback
        traceback.print_exc()

# Callback cuando se pierde la conexión MQTT
def _on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"MQTT desconectado inesperadamente, código: {rc}")

# Cliente MQTT global
_client = None

# Inicia el cliente MQTT en un hilo aparte
def iniciar_mqtt():
    global _client
    _client = mqtt.Client()
    _client.on_connect    = _on_connect
    _client.on_message    = _on_message
    _client.on_disconnect = _on_disconnect

    try:
        _client.connect(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
        # loop_start corre el bucle MQTT sin bloquear el resto de la app
        _client.loop_start()
        print("MQTT iniciado en hilo secundario")
    except Exception as e:
        print(f"MQTT no pudo conectar: {e} — continuando sin MQTT")

# Cierra el cliente MQTT
def detener_mqtt():
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        print("MQTT detenido")
