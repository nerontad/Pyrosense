# Servicio de visión por computadora: carga modelo ONNX y realiza inferencia de detección de fuego/humo
import cv2
import numpy as np
import onnxruntime as ort
import os
import gdown
from collections import deque
from app.config import get_settings

settings = get_settings()

def descargar_modelo():
    # Descargar modelo ONNX desde Google Drive si no existe localmente
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

class VisionService:
    def __init__(self):
        self.modelo      = None
        # Buffer circular para guardar últimos frames
        self.buffer: deque = deque(maxlen=settings.buffer_seconds * 20)
        self.clases      = ["fire", "smoke"]
        descargar_modelo()
        self._cargar_modelo()

    def _cargar_modelo(self):
        # Cargar modelo ONNX para CPU
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
        # Preparar frame para el modelo: redimensionar, normalizar y cambiar formato
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img

    def inferir(self, frame: np.ndarray) -> list:
        # Ejecutar inferencia en el frame y retornar detecciones
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
        # Procesar salida del modelo y filtrar por confianza
        detecciones = []
        salida = np.squeeze(salida)
        if salida.ndim == 1:
            return []

        # Transponer si necesario
        if salida.shape[0] < salida.shape[1]:
            salida = salida.T

        for fila in salida:
            scores    = fila[4:]
            clase_id  = int(np.argmax(scores))
            confianza = float(scores[clase_id])

            # Solo incluir detecciones con confianza superior al umbral
            if confianza >= settings.confidence_threshold:
                x, y, w, h = fila[:4]
                detecciones.append({
                    "clase":     self.clases[clase_id] if clase_id < len(self.clases) else str(clase_id),
                    "confianza": round(confianza, 4),
                    "bbox":      [float(x), float(y), float(w), float(h)]
                })
        return detecciones

    def agregar_al_buffer(self, frame: np.ndarray):
        # Guardar frame en buffer para reproducción posterior
        self.buffer.append(frame.copy())

    def obtener_buffer(self) -> list:
        # Retornar todos los frames en el buffer
        return list(self.buffer)

    def modelo_cargado(self) -> bool:
        # Verificar si el modelo se cargó correctamente
        return self.modelo is not None


# Instancia global del servicio de visión
vision = VisionService()