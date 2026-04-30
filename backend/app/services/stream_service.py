import cv2
import threading
import time
from app.services.vision_service import vision
from app.services.motor_alertas import procesar_deteccion

# Registro de streams activos por cámara
_streams_activos: dict = {}

class StreamProcessor:
    def __init__(self, camara_id: str, url_rtsp: str):
        self.camara_id  = camara_id
        self.url_rtsp   = url_rtsp
        self.activo     = False
        self._hilo      = None
        self.fps_proceso = 2  # Procesar 2 frames por segundo para no saturar CPU

    def iniciar(self):
        if self.activo:
            return
        self.activo = True
        self._hilo = threading.Thread(target=self._procesar, daemon=True)
        self._hilo.start()
        print(f"Stream iniciado: {self.camara_id} — {self.url_rtsp}")

    def detener(self):
        self.activo = False
        print(f"Stream detenido: {self.camara_id}")

    def _procesar(self):
        cap = cv2.VideoCapture(self.url_rtsp)
        if not cap.isOpened():
            print(f"No se pudo abrir stream: {self.url_rtsp}")
            self.activo = False
            return

        intervalo = 1.0 / self.fps_proceso
        ultimo_proceso = 0

        while self.activo:
            ret, frame = cap.read()
            if not ret:
                print(f"Stream perdido: {self.url_rtsp} — reintentando...")
                time.sleep(3)
                cap = cv2.VideoCapture(self.url_rtsp)
                continue

            # Siempre agregar al buffer circular
            vision.agregar_al_buffer(frame)

            # Inferencia a fps_proceso FPS para no saturar la CPU
            ahora = time.time()
            if (ahora - ultimo_proceso) >= intervalo:
                ultimo_proceso = ahora
                detecciones = vision.inferir(frame)
                if detecciones:
                    procesar_deteccion(self.camara_id, detecciones)

        cap.release()
        print(f"Stream cerrado: {self.camara_id}")


def iniciar_stream(camara_id: str, url_rtsp: str):
    if camara_id in _streams_activos:
        print(f"Stream {camara_id} ya está activo")
        return
    processor = StreamProcessor(camara_id, url_rtsp)
    processor.iniciar()
    _streams_activos[camara_id] = processor

def detener_stream(camara_id: str):
    if camara_id in _streams_activos:
        _streams_activos[camara_id].detener()
        del _streams_activos[camara_id]

def detener_todos():
    for camara_id in list(_streams_activos.keys()):
        detener_stream(camara_id)

def streams_activos() -> list:
    return list(_streams_activos.keys())