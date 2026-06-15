"""Tests unitarios del webhook de Telegram (comando /start).

Verifica la normalización del comando y que solo se responde a /start,
sin tocar la API real de Telegram (se mockea _responder).

Nota: webhook() es una corutina async. Para no añadir la dependencia
pytest-asyncio, las corutinas se ejecutan con asyncio.run() dentro de
cada test síncrono.
"""

import asyncio
import pytest
from app.routers import telegram


class _FakeRequest:
    """Simula un fastapi.Request con el JSON dado."""
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data


@pytest.fixture
def capturar_respuestas(monkeypatch):
    """Mockea _responder para registrar a qué chat y con qué texto se respondió,
    sin llamar a la API de Telegram."""
    enviados = []

    async def _fake_responder(chat_id, texto):
        enviados.append({"chat_id": chat_id, "texto": texto})

    monkeypatch.setattr(telegram, "_responder", _fake_responder)
    return enviados


def _mensaje(chat_id, texto):
    return _FakeRequest({"message": {"chat": {"id": chat_id}, "text": texto}})


def _mock_usuario(monkeypatch, devuelve):
    """Mockea la búsqueda de usuario por chat_id en el repositorio."""
    monkeypatch.setattr(telegram.usuario_repo,
                        "obtener_por_telegram_chat_id",
                        lambda chat_id: devuelve)


class TestWebhookStart:
    def test_start_usuario_nuevo_devuelve_chat_id(self, monkeypatch, capturar_respuestas):
        # Usuario no vinculado: el repo devuelve None
        _mock_usuario(monkeypatch, None)
        asyncio.run(telegram.webhook(_mensaje(12345, "/start")))
        assert len(capturar_respuestas) == 1
        # Debe incluir el chat_id en el mensaje de bienvenida
        assert "12345" in capturar_respuestas[0]["texto"]

    def test_start_usuario_existente_saluda_por_nombre(self, monkeypatch, capturar_respuestas):
        _mock_usuario(monkeypatch, {"id": "u1", "nombre": "Pedro"})
        asyncio.run(telegram.webhook(_mensaje(999, "/start")))
        assert "Pedro" in capturar_respuestas[0]["texto"]

    def test_start_con_arroba_bot_funciona(self, monkeypatch, capturar_respuestas):
        # "/start@MiBot" debe tratarse igual que "/start"
        _mock_usuario(monkeypatch, None)
        asyncio.run(telegram.webhook(_mensaje(7, "/start@DetectorIncendiosBot")))
        assert len(capturar_respuestas) == 1

    def test_start_con_argumento_funciona(self, monkeypatch, capturar_respuestas):
        # "/start algo" debe seguir disparando el comando
        _mock_usuario(monkeypatch, None)
        asyncio.run(telegram.webhook(_mensaje(7, "/start codigo123")))
        assert len(capturar_respuestas) == 1

    def test_otro_comando_no_responde(self, monkeypatch, capturar_respuestas):
        _mock_usuario(monkeypatch, None)
        asyncio.run(telegram.webhook(_mensaje(7, "/ayuda")))
        assert len(capturar_respuestas) == 0

    def test_mensaje_sin_chat_id_se_ignora(self, monkeypatch, capturar_respuestas):
        _mock_usuario(monkeypatch, None)
        # chat sin id
        req = _FakeRequest({"message": {"chat": {}, "text": "/start"}})
        resultado = asyncio.run(telegram.webhook(req))
        assert resultado == {"ok": True}
        assert len(capturar_respuestas) == 0

    def test_siempre_devuelve_ok(self, monkeypatch, capturar_respuestas):
        # Telegram espera 200 OK siempre, aunque el payload sea raro
        _mock_usuario(monkeypatch, None)
        resultado = asyncio.run(telegram.webhook(_FakeRequest({})))
        assert resultado == {"ok": True}
