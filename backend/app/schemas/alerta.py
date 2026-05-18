from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esquema de respuesta para un registro de alerta de incendio
class AlertaResponse(BaseModel):
    id: str
    camara_id: str
    dispositivo_id: Optional[str] = None
    tipo_id: int
    confianza: float
    revisado: bool
    ocurrido_en: datetime

# Esquema para un video asociado a una alerta
class VideoAlertaResponse(BaseModel):
    id: str
    alerta_id: str
    ruta_archivo: str
    duracion_seg: int
    tamano_bytes: int
    enviado_telegram: bool
    creado_en: datetime

# Esquema con detalles completos de una alerta incluyendo video
class AlertaDetalle(AlertaResponse):
    video: Optional[VideoAlertaResponse] = None