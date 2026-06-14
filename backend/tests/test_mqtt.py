"""Tests unitarios del procesamiento de mensajes MQTT y cooldown de alertas.

(Los umbrales en sí se prueban aparte en test_mqtt_umbrales.py.)
"""

import json
import time
import pytest
from app.services import mqtt_client


@pytest.fixture(autouse=True)
def _reset_estado():
    """Limpia el estado global del módulo antes de cada test para que no
    se filtren timers/cooldowns entre pruebas."""
    mqtt_client._ultimo_guardado_ts = 0.0
    mqtt_client._ultima_alerta_por_disp.clear()
    mqtt_client.ultimas_lecturas.clear()
    yield


# --- _guardar_lectura: normalización del campo CO2 ---
class TestGuardarLectura:
    def test_acepta_co2_directo(self, fake_execute):
        # Parchea las funciones tal como las usa el módulo mqtt_client
        import app.services.mqtt_client as m
        registradas = []
        m.execute_query = lambda sql, params=None, fetch=False: registradas.append((sql, params))
        lectura = m._guardar_lectura("disp-1", {"temperatura": 25, "humedad": 50, "co2": 800})
        assert lectura["co2_ppm"] == 800
        assert lectura["dispositivo_id"] == "disp-1"

    def test_usa_gas_si_no_hay_co2(self, fake_execute):
        # Firmware viejo manda `gas` en vez de `co2`
        import app.services.mqtt_client as m
        m.execute_query = lambda sql, params=None, fetch=False: None
        lectura = m._guardar_lectura("disp-1", {"temperatura": 25, "humedad": 50, "gas": 1200})
        assert lectura["co2_ppm"] == 1200

    def test_genera_id_unico_por_lectura(self, fake_execute):
        import app.services.mqtt_client as m
        m.execute_query = lambda sql, params=None, fetch=False: None
        l1 = m._guardar_lectura("d", {"temperatura": 20})
        l2 = m._guardar_lectura("d", {"temperatura": 20})
        assert l1["id"] != l2["id"]


# --- _generar_alerta_sensor: cooldown ---
class TestCooldownAlerta:
    def test_segunda_alerta_inmediata_es_bloqueada(self, monkeypatch):
        import app.services.mqtt_client as m
        inserts = []
        monkeypatch.setattr(m, "execute_query",
                            lambda sql, params=None, fetch=False: inserts.append(params))
        # _generar_alerta_sensor consulta el chat de Telegram con execute_one
        # y delega en el notificador (Strategy); ambos se mockean para aislar
        # la prueba del cooldown de la BD/red reales.
        monkeypatch.setattr(m, "execute_one", lambda *a, **k: None)
        monkeypatch.setattr(m._notificador, "notificar", lambda payload: None)

        m._generar_alerta_sensor("disp-X", "temperatura alta")
        # Inmediatamente después, el cooldown debe impedir un segundo insert
        m._generar_alerta_sensor("disp-X", "temperatura alta")

        assert len(inserts) == 1  # solo la primera pasó

    def test_dispositivos_distintos_no_comparten_cooldown(self, monkeypatch):
        import app.services.mqtt_client as m
        inserts = []
        monkeypatch.setattr(m, "execute_query",
                            lambda sql, params=None, fetch=False: inserts.append(params))
        monkeypatch.setattr(m, "execute_one", lambda *a, **k: None)
        monkeypatch.setattr(m._notificador, "notificar", lambda payload: None)

        m._generar_alerta_sensor("disp-A", "motivo")
        m._generar_alerta_sensor("disp-B", "motivo")

        assert len(inserts) == 2  # cada dispositivo alerta por su cuenta


# --- _on_message: parsing y validación de payload ---
class TestOnMessage:
    def _msg(self, payload_dict):
        """Construye un objeto mensaje MQTT falso con el payload dado."""
        class _Msg:
            payload = json.dumps(payload_dict).encode("utf-8")
        return _Msg()

    def test_payload_sin_dispositivo_id_se_ignora(self, monkeypatch):
        import app.services.mqtt_client as m
        llamado = {"guardar": False}
        monkeypatch.setattr(m, "execute_one", lambda *a, **k: {"id": "x"})
        monkeypatch.setattr(m, "_guardar_lectura",
                            lambda *a, **k: llamado.update(guardar=True))
        m._on_message(None, None, self._msg({"temperatura": 25}))
        assert llamado["guardar"] is False

    def test_dispositivo_inexistente_no_guarda(self, monkeypatch):
        import app.services.mqtt_client as m
        llamado = {"guardar": False}
        # execute_one devuelve None => dispositivo no existe/ inactivo
        monkeypatch.setattr(m, "execute_one", lambda *a, **k: None)
        monkeypatch.setattr(m, "_guardar_lectura",
                            lambda *a, **k: llamado.update(guardar=True))
        m._on_message(None, None, self._msg({"dispositivo_id": "fantasma", "temperatura": 25}))
        assert llamado["guardar"] is False

    def test_payload_no_json_no_rompe(self, monkeypatch):
        import app.services.mqtt_client as m

        class _MsgMalo:
            payload = b"esto no es json {{{"
        # No debe lanzar excepción
        m._on_message(None, None, _MsgMalo())

    def test_lectura_actualiza_cache_en_vivo(self, monkeypatch):
        import app.services.mqtt_client as m
        monkeypatch.setattr(m, "execute_one", lambda *a, **k: {"id": "disp-1"})
        monkeypatch.setattr(m, "_guardar_lectura", lambda *a, **k: None)
        m._on_message(None, None, self._msg({
            "dispositivo_id": "disp-1", "temperatura": 30, "humedad": 40, "co2": 500
        }))
        assert "disp-1" in m.ultimas_lecturas
        assert m.ultimas_lecturas["disp-1"]["temperatura"] == 30
