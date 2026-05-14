"""Contexto del patrón Strategy: orquesta las estrategias de notificación."""
from typing import List
from app.services.notificacion.base import EstrategiaNotificacion, AlertaPayload


class Notificador:
    """Mantiene una lista de estrategias y delega el envío en cada una.

    Agregar un canal nuevo (email, SMS, push) es solo crear otra
    EstrategiaNotificacion y registrarla con `registrar()`.
    """

    def __init__(self, estrategias: List[EstrategiaNotificacion] = None):
        self._estrategias: List[EstrategiaNotificacion] = list(estrategias or [])

    def registrar(self, estrategia: EstrategiaNotificacion) -> None:
        self._estrategias.append(estrategia)

    def notificar(self, payload: AlertaPayload) -> None:
        for estrategia in self._estrategias:
            if not estrategia.puede_enviar(payload):
                print(f"Notificador: '{estrategia.nombre()}' omitido — datos insuficientes")
                continue
            try:
                estrategia.enviar(payload)
            except Exception as e:
                print(f"Notificador: estrategia '{estrategia.nombre()}' falló — {e}")
