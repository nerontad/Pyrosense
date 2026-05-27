"""Tests del schema de lecturas: serialización de fechas como UTC."""

from datetime import datetime, timezone, timedelta
from app.schemas.lectura import LecturaResponse


def _lectura(registrado_en: datetime) -> LecturaResponse:
    return LecturaResponse(
        id="abc-123",
        dispositivo_id="dev-1",
        temperatura=20.0,
        humedad=55.0,
        co2_ppm=400.0,
        registrado_en=registrado_en,
    )


class TestSerializerUTC:
    def test_datetime_naive_se_serializa_como_utc(self):
        # MySQL devuelve DATETIME naive; el serializer le agrega UTC
        naive = datetime(2026, 5, 27, 3, 49, 25)
        data = _lectura(naive).model_dump()
        # El sufijo +00:00 garantiza que el frontend lo interprete como UTC
        assert "+00:00" in data["registrado_en"]

    def test_datetime_aware_no_se_altera(self):
        # Si ya viene con timezone, debe conservarlo
        aware = datetime(2026, 5, 27, 3, 49, 25, tzinfo=timezone.utc)
        data = _lectura(aware).model_dump()
        assert "+00:00" in data["registrado_en"]

    def test_datetime_con_offset_distinto_a_utc(self):
        # Si llegara un datetime con offset arbitrario, se conserva ese offset
        chile_winter = timezone(timedelta(hours=-4))
        aware = datetime(2026, 5, 27, 0, 0, 0, tzinfo=chile_winter)
        data = _lectura(aware).model_dump()
        assert "-04:00" in data["registrado_en"]

    def test_formato_es_iso8601(self):
        # La salida debe poder parsearse con fromisoformat (estándar ISO)
        naive = datetime(2026, 1, 1, 12, 0, 0)
        data = _lectura(naive).model_dump()
        # No lanza
        datetime.fromisoformat(data["registrado_en"])
