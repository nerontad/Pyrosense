"""Tests del patrón Strategy de notificaciones.

Verifica el contexto Notificador, el filtrado por puede_enviar(), el
aislamiento de fallos entre estrategias, y que el motor de alertas use
realmente el patrón.
"""

from app.services.notificacion import (
    Notificador,
    AlertaPayload,
    NotificacionTelegram,
    NotificacionWebSocket,
    EstrategiaNotificacion,
)


def _payload(**kw):
    base = dict(alerta_id="a1", camara_id="c1", clase="fire", confianza=0.9)
    base.update(kw)
    return AlertaPayload(**base)


class _EspiaEstrategia(EstrategiaNotificacion):
    """Estrategia de prueba que registra si fue invocada."""
    def __init__(self, puede=True, falla=False):
        self.enviado = False
        self._puede = puede
        self._falla = falla

    def nombre(self):
        return "espia"

    def puede_enviar(self, payload):
        return self._puede

    def enviar(self, payload):
        if self._falla:
            raise RuntimeError("fallo simulado")
        self.enviado = True


class TestNotificador:
    def test_invoca_estrategia_que_puede_enviar(self):
        espia = _EspiaEstrategia(puede=True)
        Notificador([espia]).notificar(_payload())
        assert espia.enviado is True

    def test_omite_estrategia_que_no_puede_enviar(self):
        espia = _EspiaEstrategia(puede=False)
        Notificador([espia]).notificar(_payload())
        assert espia.enviado is False

    def test_un_fallo_no_detiene_a_las_demas(self):
        # Si una estrategia lanza excepción, las otras deben ejecutarse igual
        falla = _EspiaEstrategia(falla=True)
        ok = _EspiaEstrategia()
        Notificador([falla, ok]).notificar(_payload())
        assert ok.enviado is True  # la segunda se ejecutó pese al fallo de la primera

    def test_registrar_agrega_estrategia(self):
        n = Notificador()
        espia = _EspiaEstrategia()
        n.registrar(espia)
        n.notificar(_payload())
        assert espia.enviado is True


class TestEstrategiasConcretas:
    def test_telegram_requiere_chat_id(self):
        tg = NotificacionTelegram()
        # Sin chat -> no puede enviar
        assert tg.puede_enviar(_payload()) is False
        # Con chat y video (alerta de cámara) -> sí puede
        assert tg.puede_enviar(
            _payload(chat_id_destino="123", ruta_video="v.mp4")
        ) is True
        # Con chat pero SIN video (alerta de sensor) -> también puede (texto)
        assert tg.puede_enviar(_payload(chat_id_destino="123")) is True

    def test_websocket_siempre_puede_enviar(self):
        ws = NotificacionWebSocket()
        assert ws.puede_enviar(_payload()) is True


class TestMotorUsaElPatron:
    def test_motor_alertas_tiene_notificador_configurado(self):
        # Evidencia de que el patrón está CONECTADO al motor real
        from app.services import motor_alertas
        assert hasattr(motor_alertas, "_notificador")
        assert isinstance(motor_alertas._notificador, Notificador)
