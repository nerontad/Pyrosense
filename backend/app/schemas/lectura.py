from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Lectura de sensor devuelta al cliente
class LecturaResponse(BaseModel):
    id: str
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None
    registrado_en: datetime

# Datos para insertar una lectura nueva
class LecturaCreate(BaseModel):
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None
