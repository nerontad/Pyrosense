"""Tests unitarios del Non-Max Suppression (NMS) del endpoint de visión.

Prueba la lógica de filtrado de cajas duplicadas sin necesitar el modelo ONNX.
"""

from app.routers.vision import _nms


def _det(cx, cy, w, h, conf, clase="fire"):
    return {"clase": clase, "confianza": conf, "bbox": [cx, cy, w, h]}


class TestNMS:
    def test_lista_vacia_devuelve_vacia(self):
        assert _nms([]) == []

    def test_una_sola_caja_se_conserva(self):
        dets = [_det(100, 100, 50, 50, 0.9)]
        assert len(_nms(dets)) == 1

    def test_dos_cajas_muy_solapadas_se_reduce_a_una(self):
        # Dos cajas casi idénticas -> NMS debe quedarse con una
        dets = [
            _det(100, 100, 50, 50, 0.9),
            _det(101, 101, 50, 50, 0.7),
        ]
        assert len(_nms(dets)) == 1

    def test_conserva_la_caja_de_mayor_confianza(self):
        dets = [
            _det(100, 100, 50, 50, 0.6),
            _det(100, 100, 50, 50, 0.95),
        ]
        resultado = _nms(dets)
        assert len(resultado) == 1
        assert resultado[0]["confianza"] == 0.95

    def test_dos_cajas_separadas_se_conservan_ambas(self):
        # Cajas en zonas distintas de la imagen -> no se solapan
        dets = [
            _det(50, 50, 40, 40, 0.9),
            _det(500, 500, 40, 40, 0.8),
        ]
        assert len(_nms(dets)) == 2
