"""Tests unitarios de los umbrales de incendio en el cliente MQTT."""

from app.services import mqtt_client


class TestDetectarUmbral:
    def test_lectura_normal_no_dispara_alerta(self):
        datos = {"temperatura": 22.0, "humedad": 55, "co2": 400}
        assert mqtt_client._detectar_umbral(datos) is None

    def test_temperatura_excede_umbral(self):
        datos = {"temperatura": 60.0, "humedad": 55, "co2": 400}
        motivo = mqtt_client._detectar_umbral(datos)
        assert motivo is not None
        assert "temperatura" in motivo.lower()

    def test_temperatura_justo_en_umbral_no_dispara(self):
        # 50.0 NO supera 50.0 (la condición es > estricto)
        datos = {"temperatura": 50.0, "humedad": 55, "co2": 400}
        assert mqtt_client._detectar_umbral(datos) is None

    def test_humedad_bajo_umbral(self):
        datos = {"temperatura": 22.0, "humedad": 15, "co2": 400}
        motivo = mqtt_client._detectar_umbral(datos)
        assert motivo is not None
        assert "humedad" in motivo.lower()

    def test_co2_excede_umbral(self):
        datos = {"temperatura": 22.0, "humedad": 55, "co2": 1500}
        motivo = mqtt_client._detectar_umbral(datos)
        assert motivo is not None
        assert "co2" in motivo.lower()

    def test_acepta_campo_gas_como_alias_de_co2(self):
        # Firmware viejo manda `gas` en lugar de `co2`
        datos = {"temperatura": 22.0, "humedad": 55, "gas": 1500}
        motivo = mqtt_client._detectar_umbral(datos)
        assert motivo is not None
        assert "co2" in motivo.lower()

    def test_temperatura_tiene_prioridad_sobre_humedad(self):
        # Si dos pasan, devuelve la primera detectada (temperatura)
        datos = {"temperatura": 70.0, "humedad": 10, "co2": 2000}
        motivo = mqtt_client._detectar_umbral(datos)
        assert "temperatura" in motivo.lower()

    def test_datos_parciales_no_rompen(self):
        # Sólo temperatura, sin humedad ni CO2 — no debe lanzar
        datos = {"temperatura": 22.0}
        assert mqtt_client._detectar_umbral(datos) is None
