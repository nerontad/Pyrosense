"""Tests del motor de alertas: cooldown entre alertas de la misma cámara."""

import pytest
from app.services import motor_alertas


@pytest.fixture(autouse=True)
def _reset_cooldown():
    # Cada test arranca con el diccionario de cooldowns vacío
    motor_alertas._cooldown.clear()
    yield
    motor_alertas._cooldown.clear()


class TestCooldown:
    def test_camara_nueva_no_esta_en_cooldown(self):
        assert motor_alertas._en_cooldown("cam-1") is False

    def test_registrar_cooldown_activa_la_espera(self):
        motor_alertas._registrar_cooldown("cam-1")
        assert motor_alertas._en_cooldown("cam-1") is True

    def test_cooldown_expira_pasado_el_tiempo(self, monkeypatch):
        motor_alertas._registrar_cooldown("cam-1")
        # Simula que pasaron COOLDOWN_SEGUNDOS + 1 desde el registro
        ts_falso = motor_alertas._cooldown["cam-1"] + motor_alertas.COOLDOWN_SEGUNDOS + 1

        import time as time_mod
        monkeypatch.setattr(time_mod, "time", lambda: ts_falso)
        assert motor_alertas._en_cooldown("cam-1") is False

    def test_cooldown_es_por_camara(self):
        motor_alertas._registrar_cooldown("cam-1")
        # cam-2 no se ve afectada por el cooldown de cam-1
        assert motor_alertas._en_cooldown("cam-2") is False
