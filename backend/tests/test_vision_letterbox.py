"""Tests del preprocesado letterbox del servicio de visión.

El letterbox redimensiona manteniendo proporción y rellena a 640x640.
Se prueba la lógica geométrica sin cargar el modelo ONNX: se invoca el
método _letterbox sobre una instancia "vacía" (sin pasar por __init__,
que descargaría el modelo).
"""

import numpy as np
from app.services.vision_service import VisionService


def _letterbox(frame):
    """Invoca VisionService._letterbox sin ejecutar __init__ (que carga el
    modelo). __new__ crea la instancia sin inicializar."""
    inst = VisionService.__new__(VisionService)
    return inst._letterbox(frame)


class TestLetterbox:
    def test_salida_siempre_640x640(self):
        # Una imagen rectangular cualquiera -> lienzo cuadrado 640x640
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        lienzo, escala = _letterbox(frame)
        assert lienzo.shape == (640, 640, 3)

    def test_imagen_horizontal_escala_por_el_ancho(self):
        # 640x360: el lado mayor es 640 -> escala = 1.0
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        _, escala = _letterbox(frame)
        assert escala == 640 / 640  # = 1.0

    def test_imagen_vertical_escala_por_el_alto(self):
        # 1000x500: lado mayor 1000 -> escala = 640/1000 = 0.64
        frame = np.zeros((1000, 500, 3), dtype=np.uint8)
        _, escala = _letterbox(frame)
        assert abs(escala - 0.64) < 1e-9

    def test_relleno_es_gris_114(self):
        # Imagen horizontal: las filas de abajo quedan como relleno gris 114
        frame = np.zeros((320, 640, 3), dtype=np.uint8)  # se escala a 640x320
        lienzo, _ = _letterbox(frame)
        # La última fila (más allá de la imagen) debe ser relleno 114
        assert (lienzo[639] == 114).all()

    def test_conserva_proporcion_sin_deformar(self):
        # Imagen 800x400 (2:1). Tras escalar, el contenido ocupa 640x320,
        # manteniendo la proporción 2:1 (no se estira a 640x640).
        frame = np.full((400, 800, 3), 50, dtype=np.uint8)
        lienzo, escala = _letterbox(frame)
        alto_contenido = int(round(400 * escala))
        ancho_contenido = int(round(800 * escala))
        assert (ancho_contenido, alto_contenido) == (640, 320)

    def test_imagen_cuadrada_llena_todo(self):
        # Imagen ya cuadrada: escala a 640x640 sin relleno
        frame = np.full((500, 500, 3), 80, dtype=np.uint8)
        lienzo, escala = _letterbox(frame)
        assert escala == 640 / 500
        # No debería haber relleno gris (todo el lienzo es contenido)
        assert not (lienzo == 114).all()
