import cv2
import numpy as np
import onnxruntime as ort
from collections import deque
from app.config import get_settings

settings = get_settings()

class VisionService:
    def __init__(self):
        self.modelo = None
        self.buffer: deque = deque(maxlen=settings.buffer_seconds * 20)
        self.clases = ["fire", "smoke"]
        self._cargar_modelo()

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

    def preprocesar_frame(self, frame: np.ndarray) -> np.ndarray:
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img

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

    def _procesar_salida(self, salida: np.ndarray) -> list:
        detecciones = []
        # YOLOv8 ONNX — salida shape: [1, num_clases+4, num_anchors]
        salida = np.squeeze(salida)
        if salida.ndim == 1:
            return []

        # Transponer si es necesario
        if salida.shape[0] < salida.shape[1]:
            salida = salida.T

        for fila in salida:
            scores = fila[4:]
            clase_id = int(np.argmax(scores))
            confianza = float(scores[clase_id])

            if confianza >= settings.confidence_threshold:
                x, y, w, h = fila[:4]
                detecciones.append({
                    "clase":     self.clases[clase_id] if clase_id < len(self.clases) else str(clase_id),
                    "confianza": round(confianza, 4),
                    "bbox":      [float(x), float(y), float(w), float(h)]
                })
        return detecciones

    def agregar_al_buffer(self, frame: np.ndarray):
        self.buffer.append(frame.copy())

    def obtener_buffer(self) -> list:
        return list(self.buffer)

    def modelo_cargado(self) -> bool:
        return self.modelo is not None


# Instancia global — se reutiliza en todo el backend
vision = VisionService()