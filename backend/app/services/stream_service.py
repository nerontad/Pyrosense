# Servicio de streaming: captura video RTSP, realiza inferencia y guarda buffer de detecciones
import cv2
import threading
import time
import subprocess
from app.services.vision_service import vision
from app.services.motor_alertas import procesar_deteccion

# Diccionario de streams activos: {camara_id: StreamProcessor}
_streams_activos: dict = {}

class StreamProcessor:
    def __init__(self, camara_id: str, url_rtsp: str):
        self.camara_id   = camara_id
        self.url_rtsp    = url_rtsp
        self.activo      = False
        self._hilo       = None
        self._ffmpeg     = None
        self.fps_proceso = 2

    def iniciar(self):
        # Iniciar stream en hilo separado
        if self.activo:
            return
        self.activo = True
        self._iniciar_ffmpeg()
        self._hilo = threading.Thread(target=self._procesar, daemon=True)
        self._hilo.start()
        print(f"Stream iniciado: {self.camara_id}")

    def _iniciar_ffmpeg(self):
        # Iniciar ffmpeg en hilo separado para retransmitir video
        hilo = threading.Thread(target=self._ffmpeg_loop, daemon=True)
        hilo.start()
        print(f"ffmpeg iniciado para: {self.camara_id}")
        time.sleep(5)

    def _ffmpeg_loop(self):
        # Loop infinito: capturar RTSP y retransmitir a VPS
        while self.activo:
            cmd = [
                "ffmpeg",
                "-rtsp_transport", "tcp",
                "-timeout", "10000000",
                "-i", self.url_rtsp,
                "-c:v", "copy",
                "-c:a", "copy",
                "-f", "rtsp",
                "-rtsp_transport", "tcp",
                f"rtsp://159.223.189.120:8554/{self.camara_id}",
                "-y"
            ]
            print(f"ffmpeg conectando a: {self.url_rtsp}")
            self._ffmpeg = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._ffmpeg.wait()

            if self.activo:
                print(f"ffmpeg caído para {self.camara_id} — reintentando en 5s...")
                time.sleep(5)

        print(f"ffmpeg_loop terminado: {self.camara_id}")

    def detener(self):
        # Detener captura y ffmpeg
        self.activo = False
        if self._ffmpeg:
            self._ffmpeg.terminate()
            self._ffmpeg = None
        print(f"Stream detenido: {self.camara_id}")

    def _procesar(self):
        # Leer video del VPS, inferir y procesar detecciones
        url_lectura = f"rtsp://159.223.189.120:8554/{self.camara_id}"

        # Esperar a que ffmpeg establezca la retransmisión
        time.sleep(15)
        
        while self.activo:
            cap = cv2.VideoCapture(url_lectura)
            if not cap.isOpened():
                print(f"Stream VPS no disponible aún — esperando 10s...")
                time.sleep(10)
                continue

            print(f"Stream VPS conectado: {url_lectura}")
            intervalo = 1.0 / self.fps_proceso
            ultimo    = 0

            while self.activo:
                ret, frame = cap.read()
                if not ret:
                    print(f"Stream VPS perdido — reconectando...")
                    cap.release()
                    time.sleep(5)
                    break

                # Guardar frame en buffer para video de alerta
                vision.agregar_al_buffer(frame)

                # Procesar frame según velocidad configurada
                ahora = time.time()
                if (ahora - ultimo) >= intervalo:
                    ultimo = ahora
                    # Ejecutar modelo de IA sobre frame
                    detecciones = vision.inferir(frame)
                    if detecciones:
                        # Disparar flujo de generación de alerta
                        procesar_deteccion(self.camara_id, detecciones)

            if cap.isOpened():
                cap.release()

        print(f"Stream cerrado: {self.camara_id}")


def iniciar_stream(camara_id: str, url_rtsp: str):
    # Crear y iniciar nuevo procesador de stream
    if camara_id in _streams_activos:
        print(f"Stream {camara_id} ya está activo")
        return
    processor = StreamProcessor(camara_id, url_rtsp)
    processor.iniciar()
    _streams_activos[camara_id] = processor

def detener_stream(camara_id: str):
    # Detener stream específico
    if camara_id in _streams_activos:
        _streams_activos[camara_id].detener()
        del _streams_activos[camara_id]

def detener_todos():
    # Detener todos los streams activos
    for camara_id in list(_streams_activos.keys()):
        detener_stream(camara_id)

def streams_activos() -> list:
    # Retornar lista de IDs de streams activos
    return list(_streams_activos.keys())