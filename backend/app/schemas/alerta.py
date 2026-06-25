from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime, timezone


# La BD guarda los DATETIME en UTC pero sin zona horaria (naive). Este
# serializer les agrega el offset UTC (+00:00) para que el frontend los
# convierta correctamente a la hora local y no sume horas de más.
def _serializar_utc(v: datetime) -> str:
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat()


# Alerta básica detectada por la IA
class AlertaResponse(BaseModel):
    id: str
    camara_id: str
    dispositivo_id: Optional[str] = None
    tipo_id: int
    confianza: float
    revisado: bool
    ocurrido_en: datetime

    @field_serializer("ocurrido_en")
    def _ser_ocurrido_en(self, v: datetime) -> str:
        return _serializar_utc(v)

# Metadatos del video grabado al detectarse una alerta
class VideoAlertaResponse(BaseModel):
    id: str
    alerta_id: str
    ruta_archivo: str
    duracion_seg: int
    tamano_bytes: int
    enviado_telegram: bool
    creado_en: datetime

    @field_serializer("creado_en")
    def _ser_creado_en(self, v: datetime) -> str:
        return _serializar_utc(v)

# Alerta con el video adjunto (vista de detalle)
class AlertaDetalle(AlertaResponse):
    video: Optional[VideoAlertaResponse] = None
