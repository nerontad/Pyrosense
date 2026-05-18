from abc import ABC, abstractmethod


class NotificadorAlerta(ABC):
    """Interfaz del patrón Strategy para canales de notificación.

    Cada canal (WebSocket, Telegram, Firebase, ...) implementa esta
    interfaz. El motor de alertas solo conoce el contrato `enviar(alerta)`
    y delega en la lista de notificadores registrados, sin saber el
    detalle de cada canal.
    """

    @abstractmethod
    def enviar(self, alerta: dict) -> None:
        """Envía la alerta por el canal correspondiente.

        Espera un dict con al menos:
          - alerta_id (str)
          - camara_id (str)          - clase (str)         "fire" | "smoke"
          - confianza (float)
          - datos_video (dict|None) opcional: {ruta_archivo, duracion_seg, tamano_bytes}
        """
        raise NotImplementedError
