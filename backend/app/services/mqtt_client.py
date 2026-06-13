import json
import time
import uuid
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from app.config import get_settings
from app.database.connection import execute_query, execute_one
from app.services.notificacion import (
    Notificador,
    AlertaPayload,
    NotificacionTelegram,
    NotificacionWebSocket,
)

settings = get_settings()

# Notificador (patrón Strategy) compartido para las alertas de sensores.
# Usa las mismas estrategias que el motor de alertas de cámara, de modo que
# una alerta de sensor también llega por WebSocket y Telegram.
_notificador = Notificador([
    NotificacionWebSocket(),
    NotificacionTelegram(),
])

# Intervalo mínimo entre guardados (global, todos los dispositivos)
INTERVALO_GUARDADO_S = 120

# Umbrales que fuerzan un guardado inmediato y generan alerta
UMBRAL_TEMP_MAX    = 50.0   # °C
UMBRAL_HUMEDAD_MIN = 20.0   # %
UMBRAL_CO2_MAX     = 1000.0 # ppm

# Cooldown entre alertas por dispositivo (no spamear cuando el umbral está alto)
COOLDOWN_ALERTA_S = 300  # 5 min

# Última vez que se guardó en BD (timer global)
_ultimo_guardado_ts: float = 0.0
# Última vez que se generó alerta por dispositivo
_ultima_alerta_por_disp: dict = {}

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

# Revisa si algún valor cruza los umbrales de incendio.
# Devuelve un texto con el motivo si pasa, None si está todo OK.
def _detectar_umbral(datos: dict):
    temp = datos.get("temperatura")
    hum  = datos.get("humedad")
    co2  = datos.get("co2") if datos.get("co2") is not None else datos.get("gas")
    if temp is not None and temp > UMBRAL_TEMP_MAX:
        return f"temperatura {temp}°C > {UMBRAL_TEMP_MAX}°C"
    if hum is not None and hum < UMBRAL_HUMEDAD_MIN:
        return f"humedad {hum}% < {UMBRAL_HUMEDAD_MIN}%"
    if co2 is not None and co2 > UMBRAL_CO2_MAX:
        return f"co2 {co2} ppm > {UMBRAL_CO2_MAX} ppm"
    return None

# Inserta una alerta de sensor y notifica por WebSocket (con cooldown)
def _generar_alerta_sensor(dispositivo_id: str, motivo: str):
    ahora = time.time()
    if (ahora - _ultima_alerta_por_disp.get(dispositivo_id, 0)) < COOLDOWN_ALERTA_S:
        return
    _ultima_alerta_por_disp[dispositivo_id] = ahora

    alerta_id = str(uuid.uuid4())
    try:
        execute_query(
            """INSERT INTO alertas (id, dispositivo_id, tipo_id, confianza)
               VALUES (%s, %s, %s, %s)""",
            (alerta_id, dispositivo_id, 1, 1.0)
        )
        print(f"Alerta sensor guardada ({motivo}) id={alerta_id}")
    except Exception as e:
        print(f"Alerta sensor: error al insertar: {e}")
        return

    # Notifica por todos los canales con el mismo patrón Strategy que las
    # alertas de cámara. La clase usa el motivo del umbral (ej. "temperatura").
    info = _info_notificacion_sensor(dispositivo_id)
    _notificador.notificar(AlertaPayload(
        alerta_id=alerta_id,
        camara_id=dispositivo_id,   # identifica el origen de la alerta
        clase=motivo,
        confianza=1.0,
        ubicacion=info.get("ubicacion") if info else None,
        ruta_video=None,            # los sensores no graban video
        chat_id_destino=info.get("telegram_chat_id") if info else None,
    ))

# Busca el chat_id de Telegram del dueño y la ubicación del dispositivo
def _info_notificacion_sensor(dispositivo_id: str):
    return execute_one(
        """SELECT u.telegram_chat_id, ub.nombre AS ubicacion
           FROM dispositivos_iot d
           JOIN usuarios u ON u.id = d.usuario_id
           JOIN ubicaciones ub ON ub.id = d.ubicacion_id
           WHERE d.id = %s""",
        (dispositivo_id,)
    )

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

        # Normaliza el campo de CO2 (acepta `co2` o `gas` del firmware viejo)
        co2_valor = payload.get("co2")
        if co2_valor is None:
            co2_valor = payload.get("gas")

        # Actualiza la cache y notifica SIEMPRE (chart en vivo del frontend)
        ahora_utc = datetime.now(timezone.utc)
        ultimas_lecturas[dispositivo_id] = {
            "dispositivo_id": dispositivo_id,
            "temperatura": payload.get("temperatura"),
            "humedad":     payload.get("humedad"),
            "co2_ppm":     co2_valor,
            "registrado_en": ahora_utc.isoformat()
        }
        _notificar(ultimas_lecturas[dispositivo_id])

        # Decide si toca persistir: por timer global o por umbral
        global _ultimo_guardado_ts
        ahora = time.time()
        motivo_umbral = _detectar_umbral(payload)
        debe_guardar = (
            motivo_umbral is not None or
            (ahora - _ultimo_guardado_ts) >= INTERVALO_GUARDADO_S
        )

        if debe_guardar:
            lectura = _guardar_lectura(dispositivo_id, payload)
            _ultimo_guardado_ts = ahora
            motivo = motivo_umbral or f"intervalo {INTERVALO_GUARDADO_S}s"
            print(f"MQTT: lectura guardada ({motivo}): {lectura}")
            if motivo_umbral:
                _generar_alerta_sensor(dispositivo_id, motivo_umbral)
        else:
            restante = INTERVALO_GUARDADO_S - (ahora - _ultimo_guardado_ts)
            print(f"MQTT: lectura en vivo (no se persiste, faltan {restante:.0f}s)")

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
