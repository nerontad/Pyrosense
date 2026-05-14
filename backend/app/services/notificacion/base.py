"""
Patrón Strategy — interfaz para canales de notificación.

Cada canal por el que se puede notificar una alerta (Telegram, WebSocket,
y a futuro email/SMS/push) implementa esta interfaz. El motor de alertas
no conoce los detalles de cada canal: solo pide al Notificador que envíe
la alerta y este delega en las estrategias configuradas.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlertaPayload:
    """Datos que viajan a través de cualquier canal de notificación."""
    alerta_id: str
    camara_id: str
    clase: str
    confianza: float
    ubicacion: Optional[str] = None
    ruta_video: Optional[str] = None
    chat_id_destino: Optional[str] = None


class EstrategiaNotificacion(ABC):
    """Contrato común que debe cumplir cada canal de notificación."""

    @abstractmethod
    def nombre(self) -> str:
        ...

    @abstractmethod
    def puede_enviar(self, payload: AlertaPayload) -> bool:
        """Indica si esta estrategia tiene los datos para enviar."""
        ...

    @abstractmethod
    def enviar(self, payload: AlertaPayload) -> None:
        ...
