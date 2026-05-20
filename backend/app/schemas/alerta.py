from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Alerta básica detectada por la IA
class AlertaResponse(BaseModel):
    id: str
    camara_id: str
    dispositivo_id: Optional[str] = None
    tipo_id: int
    confianza: float
    revisado: bool
    ocurrido_en: datetime

# Metadatos del video grabado al detectarse una alerta
class VideoAlertaResponse(BaseModel):
    id: str
    alerta_id: str
    ruta_archivo: str
    duracion_seg: int
    tamano_bytes: int
    enviado_telegram: bool
    creado_en: datetime

# Alerta con el video adjunto (vista de detalle)
class AlertaDetalle(AlertaResponse):
    video: Optional[VideoAlertaResponse] = None
