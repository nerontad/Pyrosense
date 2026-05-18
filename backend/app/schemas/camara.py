from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esquema para crear una nueva cámara RTSP
class CamaraCreate(BaseModel):
    nombre: str
    url_rtsp: str
    ubicacion_id: str

# Esquema de respuesta con datos de la cámara
class CamaraResponse(BaseModel):
    id: str
    nombre: str
    url_rtsp: str
    ubicacion_id: str
    activo: bool
    creado_en: datetime

# Esquema para actualizar datos de la cámara
class CamaraUpdate(BaseModel):
    nombre: Optional[str] = None
    url_rtsp: Optional[str] = None
    activo: Optional[bool] = None