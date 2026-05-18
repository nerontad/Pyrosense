from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esquema de respuesta para una lectura de sensores
class LecturaResponse(BaseModel):
    id: str
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None
    registrado_en: datetime

# Esquema para crear nueva lectura de sensores
class LecturaCreate(BaseModel):
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None