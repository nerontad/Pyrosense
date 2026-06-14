"""Tests del schema de alertas: validación de tipos y herencia de AlertaDetalle."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.alerta import AlertaResponse, VideoAlertaResponse, AlertaDetalle


def _alerta_kwargs():
    return dict(
        id="a-1",
        camara_id="cam-1",
        tipo_id=1,
        confianza=0.92,
        revisado=False,
        ocurrido_en=datetime(2026, 6, 8, 12, 0, 0),
    )


class TestAlertaResponse:
    def test_crea_alerta_basica(self):
        a = AlertaResponse(**_alerta_kwargs())
        assert a.confianza == 0.92
        assert a.dispositivo_id is None  # opcional

    def test_confianza_string_numerico_se_convierte(self):
        # Pydantic v2 coacciona "0.5" -> 0.5 (float)
        kw = _alerta_kwargs()
        kw["confianza"] = "0.5"
        a = AlertaResponse(**kw)
        assert a.confianza == 0.5

    def test_tipo_id_no_numerico_lanza_error(self):
        kw = _alerta_kwargs()
        kw["tipo_id"] = "fuego"  # no convertible a int
        with pytest.raises(ValidationError):
            AlertaResponse(**kw)


class TestAlertaDetalle:
    def test_hereda_campos_de_alerta_y_video_opcional(self):
        d = AlertaDetalle(**_alerta_kwargs())
        # Hereda los campos de AlertaResponse
        assert d.camara_id == "cam-1"
        # video es opcional
        assert d.video is None

    def test_acepta_video_adjunto(self):
        video = VideoAlertaResponse(
            id="v-1",
            alerta_id="a-1",
            ruta_archivo="videos/alerta.mp4",
            duracion_seg=10,
            tamano_bytes=2048,
            enviado_telegram=True,
            creado_en=datetime(2026, 6, 8, 12, 0, 5),
        )
        d = AlertaDetalle(**_alerta_kwargs(), video=video)
        assert d.video.ruta_archivo == "videos/alerta.mp4"
        assert d.video.enviado_telegram is True
