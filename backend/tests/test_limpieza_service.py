"""Tests del servicio de limpieza de lecturas antiguas (RNF04)."""

from app.services import limpieza_service


class TestPurgaLecturasAntiguas:
    def test_constante_retencion_es_90_dias(self):
        # RNF04 exige 90 días de retención
        assert limpieza_service.DIAS_RETENCION == 90

    def test_intervalo_diario(self):
        # El job debe correr al menos una vez al día
        assert limpieza_service.INTERVALO_S == 24 * 60 * 60

    def test_purgar_emite_delete_con_intervalo_correcto(self, monkeypatch):
        consultas = []

        def fake_execute(sql, params=None, fetch=False):
            consultas.append({"sql": sql, "params": params, "fetch": fetch})
            if fetch:
                return [{"n": 3}]
            return 1

        monkeypatch.setattr(limpieza_service, "execute_query", fake_execute)
        borrados = limpieza_service.purgar_lecturas_antiguas()

        # Debe contar primero y borrar después
        assert len(consultas) == 2
        assert "COUNT" in consultas[0]["sql"]
        assert "DELETE" in consultas[1]["sql"]

        # Ambas queries usan el mismo parámetro de retención (90)
        assert consultas[0]["params"] == (90,)
        assert consultas[1]["params"] == (90,)

        # Y devuelve el conteo previo
        assert borrados == 3

    def test_purgar_devuelve_cero_si_falla(self, monkeypatch):
        def fake_execute(*args, **kwargs):
            raise RuntimeError("BD caída")

        monkeypatch.setattr(limpieza_service, "execute_query", fake_execute)
        # No debe propagar la excepción
        assert limpieza_service.purgar_lecturas_antiguas() == 0
