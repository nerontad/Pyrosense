import cv2
import numpy as np
import onnxruntime as ort
import os
import gdown
from collections import deque
from app.config import get_settings

settings = get_settings()

# Descarga el modelo ONNX desde Google Drive si no existe en disco
def descargar_modelo():
    if not os.path.exists(settings.model_path):
        os.makedirs(
            os.path.dirname(settings.model_path) if os.path.dirname(settings.model_path) else '.',
            exist_ok=True
        )
        google_drive_id = os.getenv("MODEL_DRIVE_ID", "")
        if google_drive_id:
            print(f"Descargando modelo desde Google Drive...")
            url = f"https://drive.google.com/uc?id={google_drive_id}"
            gdown.download(url, settings.model_path, quiet=False)
            print(f"Modelo descargado: {settings.model_path}")
        else:
            print("MODEL_DRIVE_ID no configurado — modelo no disponible")
    else:
        print(f"Modelo ya existe: {settings.model_path}")

# Servicio que carga el modelo YOLO ONNX y hace inferencia sobre frames
class VisionService:
    def __init__(self):
        self.modelo      = None
        # Buffer circular de los últimos N segundos de frames (para grabar clip)
        self.buffer: deque = deque(maxlen=settings.buffer_seconds * 20)
        # Clases del modelo entrenado
        self.clases      = ["fire", "smoke"]
        descargar_modelo()
        self._cargar_modelo()

    # Carga el modelo ONNX en memoria
    def _cargar_modelo(self):
        try:
            self.modelo = ort.InferenceSession(
                settings.model_path,
                providers=["CPUExecutionProvider"]
            )
            self.input_name  = self.modelo.get_inputs()[0].name
            self.input_shape = self.modelo.get_inputs()[0].shape
            print(f"Modelo ONNX cargado: {settings.model_path}")
            print(f"Input shape: {self.input_shape}")
        except Exception as e:
            print(f"Error al cargar modelo ONNX: {e}")
            self.modelo = None

    # Prepara un frame para entrar al modelo: resize, RGB, normaliza, batch
    def preprocesar_frame(self, frame: np.ndarray) -> np.ndarray:
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img

    # Ejecuta el modelo sobre un frame y devuelve las detecciones encontradas
    def inferir(self, frame: np.ndarray) -> list:
        if self.modelo is None:
            return []
        try:
            entrada = self.preprocesar_frame(frame)
            salida  = self.modelo.run(None, {self.input_name: entrada})
            return self._procesar_salida(salida[0])
        except Exception as e:
            print(f"Error en inferencia: {e}")
            return []

    # Filtra la salida del modelo y devuelve solo detecciones por encima del umbral
    def _procesar_salida(self, salida: np.ndarray) -> list:
        detecciones = []
        salida = np.squeeze(salida)
        if salida.ndim == 1:
            return []

        # Transpone si las filas y columnas vienen invertidas
        if salida.shape[0] < salida.shape[1]:
            salida = salida.T

        for fila in salida:
            scores    = fila[4:]
            clase_id  = int(np.argmax(scores))
            confianza = float(scores[clase_id])

            # Descarta detecciones débiles
            if confianza >= settings.confidence_threshold:
                x, y, w, h = fila[:4]
                detecciones.append({
                    "clase":     self.clases[clase_id] if clase_id < len(self.clases) else str(clase_id),
                    "confianza": round(confianza, 4),
                    "bbox":      [float(x), float(y), float(w), float(h)]
                })
        return detecciones

    # Guarda un frame en el buffer circular
    def agregar_al_buffer(self, frame: np.ndarray):
        self.buffer.append(frame.copy())

    # Devuelve los frames buffer (para grabar el clip de la alerta)
    def obtener_buffer(self) -> list:
        return list(self.buffer)

    # Indica si el modelo ONNX está listo
    def modelo_cargado(self) -> bool:
        return self.modelo is not None


# Instancia única usada por el resto de la app
vision = VisionService()
