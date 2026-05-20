from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Datos para registrar una cámara nueva
class CamaraCreate(BaseModel):
    nombre: str
    url_rtsp: str
    ubicacion_id: str

# Cámara devuelta al cliente
class CamaraResponse(BaseModel):
    id: str
    nombre: str
    url_rtsp: str
    ubicacion_id: str
    activo: bool
    creado_en: datetime

# Campos editables al actualizar una cámara
class CamaraUpdate(BaseModel):
    nombre: Optional[str] = None
    url_rtsp: Optional[str] = None
    activo: Optional[bool] = None
