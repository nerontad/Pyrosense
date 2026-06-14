"""Tests del schema de cámaras: validación de campos requeridos y opcionales."""

import pytest
from pydantic import ValidationError
from app.schemas.camara import CamaraCreate, CamaraUpdate


class TestCamaraCreate:
    def test_crea_con_todos_los_campos(self):
        c = CamaraCreate(
            nombre="Cámara Bodega",
            url_rtsp="rtsp://user:pass@10.0.0.1/stream",
            ubicacion_id="ubi-1",
        )
        assert c.nombre == "Cámara Bodega"
        assert c.ubicacion_id == "ubi-1"

    def test_falta_nombre_lanza_error(self):
        with pytest.raises(ValidationError):
            CamaraCreate(url_rtsp="rtsp://x", ubicacion_id="u1")

    def test_falta_url_lanza_error(self):
        with pytest.raises(ValidationError):
            CamaraCreate(nombre="Cam", ubicacion_id="u1")

    def test_falta_ubicacion_lanza_error(self):
        with pytest.raises(ValidationError):
            CamaraCreate(nombre="Cam", url_rtsp="rtsp://x")


class TestCamaraUpdate:
    def test_todos_los_campos_son_opcionales(self):
        # Update vacío es válido (no se cambia nada)
        u = CamaraUpdate()
        assert u.nombre is None
        assert u.url_rtsp is None
        assert u.activo is None

    def test_actualizar_solo_nombre(self):
        u = CamaraUpdate(nombre="Nuevo nombre")
        assert u.nombre == "Nuevo nombre"
        assert u.url_rtsp is None

    def test_activo_acepta_booleano(self):
        u = CamaraUpdate(activo=False)
        assert u.activo is False
