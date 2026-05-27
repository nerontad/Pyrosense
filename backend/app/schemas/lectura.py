from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime, timezone

# Lectura de sensor devuelta al cliente
class LecturaResponse(BaseModel):
    id: str
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None
    registrado_en: datetime

    # Muestra hora en local
    @field_serializer("registrado_en")
    def _serialize_registrado_en(self, v: datetime) -> str:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()

# Datos para insertar una lectura nueva
class LecturaCreate(BaseModel):
    dispositivo_id: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    co2_ppm: Optional[float] = None
