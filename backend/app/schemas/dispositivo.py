from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DispositivoCreate(BaseModel):
    nombre: str
    ubicacion_id: str
    tipo_id: int

class DispositivoResponse(BaseModel):
    id: str
    nombre: str
    ubicacion_id: str
    tipo_id: int
    activo: bool
    creado_en: datetime

class DispositivoUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None