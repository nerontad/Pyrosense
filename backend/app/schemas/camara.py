from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CamaraCreate(BaseModel):
    nombre: str
    url_rtsp: str
    ubicacion_id: str

class CamaraResponse(BaseModel):
    id: str
    nombre: str
    url_rtsp: str
    ubicacion_id: str
    activo: bool
    creado_en: datetime

class CamaraUpdate(BaseModel):
    nombre: Optional[str] = None
    url_rtsp: Optional[str] = None
    activo: Optional[bool] = None