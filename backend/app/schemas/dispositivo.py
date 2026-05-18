from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esquema para crear nuevo dispositivo IoT (sensor)
class DispositivoCreate(BaseModel):
    nombre: str
    ubicacion_id: str
    tipo_id: int

# Esquema de respuesta con datos del dispositivo
class DispositivoResponse(BaseModel):
    id: str
    nombre: str
    ubicacion_id: str
    tipo_id: int
    activo: bool
    creado_en: datetime

# Esquema para actualizar propiedades del dispositivo
class DispositivoUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None