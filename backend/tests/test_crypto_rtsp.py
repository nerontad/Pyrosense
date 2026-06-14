"""Tests unitarios del cifrado de URLs RTSP (credenciales de cámara).

Cubre el ciclo cifrar -> descifrar -> enmascarar y la compatibilidad con
cámaras antiguas guardadas en texto plano.
"""

from app.utils.crypto_rtsp import (
    cifrar_url,
    descifrar_url,
    enmascarar_url,
    esta_enmascarada,
    MASCARA,
)

URL = "rtsp://admin:Secreta123@192.168.1.11:554/cam/realmonitor?channel=1&subtype=0"


class TestCifrado:
    def test_la_clave_no_aparece_en_el_cifrado(self):
        cif = cifrar_url(URL)
        assert "Secreta123" not in cif
        assert cif.startswith("enc:")

    def test_descifrar_recupera_la_url_original(self):
        assert descifrar_url(cifrar_url(URL)) == URL

    def test_no_re_cifra_lo_ya_cifrado(self):
        cif = cifrar_url(URL)
        # Cifrar dos veces debe ser idempotente (no aplica enc: sobre enc:)
        assert cifrar_url(cif) == cif

    def test_cadena_vacia_no_rompe(self):
        assert cifrar_url("") == ""
        assert descifrar_url("") == ""


class TestCompatibilidadLegacy:
    def test_url_en_texto_plano_se_devuelve_igual(self):
        # Cámara antigua sin prefijo enc: -> se usa tal cual
        plana = "rtsp://user:pass@10.0.0.1/stream"
        assert descifrar_url(plana) == plana


class TestEnmascarado:
    def test_oculta_la_contrasena(self):
        masc = enmascarar_url(URL)
        assert "Secreta123" not in masc
        assert MASCARA in masc

    def test_conserva_usuario_y_host_visibles(self):
        masc = enmascarar_url(URL)
        assert "admin" in masc
        assert "192.168.1.11" in masc

    def test_url_sin_contrasena_no_cambia(self):
        sin_pass = "rtsp://192.168.1.11:554/stream"
        assert enmascarar_url(sin_pass) == sin_pass


class TestEstaEnmascarada:
    def test_detecta_url_enmascarada(self):
        assert esta_enmascarada(enmascarar_url(URL)) is True

    def test_url_real_no_se_considera_enmascarada(self):
        assert esta_enmascarada(URL) is False

    def test_cadena_vacia_no_esta_enmascarada(self):
        assert esta_enmascarada("") is False
