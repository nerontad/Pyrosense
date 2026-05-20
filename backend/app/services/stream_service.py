import cv2
import threading
import time
import subprocess
from app.services.vision_service import vision
from app.services.motor_alertas import procesar_deteccion

# Registro de streams activos por camara_id
_streams_activos: dict = {}

# Procesa un stream RTSP de una cámara y ejecuta la detección IA
class StreamProcessor:
    def __init__(self, camara_id: str, url_rtsp: str):
        self.camara_id   = camara_id
        self.url_rtsp    = url_rtsp
        self.activo      = False
        self._hilo       = None
        self._ffmpeg     = None
        # Frames por segundo que se envían al modelo IA
        self.fps_proceso = 2

    # Arranca el reenvío RTSP y el hilo de detección
    def iniciar(self):
        if self.activo:
            return
        self.activo = True
        self._iniciar_ffmpeg()
        self._hilo = threading.Thread(target=self._procesar, daemon=True)
        self._hilo.start()
        print(f"Stream iniciado: {self.camara_id}")

    # Lanza ffmpeg en un hilo separado para reenviar el RTSP al servidor público
    def _iniciar_ffmpeg(self):
        hilo = threading.Thread(target=self._ffmpeg_loop, daemon=True)
        hilo.start()
        print(f"ffmpeg iniciado para: {self.camara_id}")
        time.sleep(5)

    # Re-arranca ffmpeg automáticamente si se cae
    def _ffmpeg_loop(self):
        while self.activo:
            cmd = [
                "ffmpeg",
                "-rtsp_transport", "tcp",
                "-timeout", "10000000",
                "-i", self.url_rtsp,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "zerolatency",
                "-c:a", "aac",
                "-f", "rtsp",
                "-rtsp_transport", "tcp",
                f"rtsp://137.184.21.60:8554/{self.camara_id}",
                "-y"
            ]
            print(f"ffmpeg conectando a: {self.url_rtsp}")
            self._ffmpeg = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._ffmpeg.wait()

            # Si se cayó pero el stream sigue activo, reintenta tras 5 segundos
            if self.activo:
                print(f"ffmpeg caído para {self.camara_id} — reintentando en 5s...")
                time.sleep(5)

        print(f"ffmpeg_loop terminado: {self.camara_id}")

    # Marca el stream como inactivo y mata el proceso ffmpeg
    def detener(self):
        self.activo = False
        if self._ffmpeg:
            self._ffmpeg.terminate()
            self._ffmpeg = None
        print(f"Stream detenido: {self.camara_id}")

    # Lee frames del stream republicado y manda algunos al modelo de detección
    def _procesar(self):
        url_lectura = f"rtsp://137.184.21.60:8554/{self.camara_id}"

        # Espera a que ffmpeg termine de empujar el stream
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
                # Si se pierde el stream, reconecta desde fuera
                if not ret:
                    print(f"Stream VPS perdido — reconectando...")
                    cap.release()
                    time.sleep(5)
                    break

                # Cada frame se guarda en el buffer (para luego grabar el clip)
                vision.agregar_al_buffer(frame)

                # Solo manda al modelo cada cierto intervalo (no cada frame)
                ahora = time.time()
                if (ahora - ultimo) >= intervalo:
                    ultimo = ahora
                    detecciones = vision.inferir(frame)
                    if detecciones:
                        procesar_deteccion(self.camara_id, detecciones)

            if cap.isOpened():
                cap.release()

        print(f"Stream cerrado: {self.camara_id}")


# Crea y arranca un stream nuevo si no estaba ya activo
def iniciar_stream(camara_id: str, url_rtsp: str):
    if camara_id in _streams_activos:
        print(f"Stream {camara_id} ya está activo")
        return
    processor = StreamProcessor(camara_id, url_rtsp)
    processor.iniciar()
    _streams_activos[camara_id] = processor

# Detiene el stream de una cámara y lo quita del registro
def detener_stream(camara_id: str):
    if camara_id in _streams_activos:
        _streams_activos[camara_id].detener()
        del _streams_activos[camara_id]

# Detiene todos los streams (al cerrar la app)
def detener_todos():
    for camara_id in list(_streams_activos.keys()):
        detener_stream(camara_id)

# Lista los IDs de los streams actualmente activos
def streams_activos() -> list:
    return list(_streams_activos.keys())
