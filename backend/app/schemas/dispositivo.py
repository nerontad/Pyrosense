from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Datos para crear un dispositivo IoT
class DispositivoCreate(BaseModel):
    nombre: str
    ubicacion_id: str
    tipo_id: int

# Dispositivo IoT devuelto al cliente
class DispositivoResponse(BaseModel):
    id: str
    nombre: str
    ubicacion_id: str
    tipo_id: int
    activo: bool
    creado_en: datetime

# Campos editables al actualizar un dispositivo
class DispositivoUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None
