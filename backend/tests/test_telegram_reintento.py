"""
PR-05 — Reintento automático de alerta fallida por Telegram.

Se simula una interrupción de conectividad durante el envío del video de
alerta y se verifica que el sistema reintenta automáticamente hasta agotar
MAX_REINTENTOS, usando backoff exponencial entre cada intento.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from telegram.error import TelegramError

from app.services.telegram_service import (
    _enviar_video_async,
    MAX_REINTENTOS,
    ESPERA_BASE_S,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def video_fake(tmp_path):
    """Crea un archivo de video temporal para las pruebas."""
    v = tmp_path / "alerta_test.mp4"
    v.write_bytes(b"\x00" * 64)   # contenido mínimo
    return str(v)


def _correr(coro):
    """Ejecuta una corutina de forma síncrona (compatible con pytest sin asyncio)."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ─── Helper para parchear Bot y asyncio.sleep ─────────────────────────────

def _mock_contexto(send_video_side_effect, monkeypatch):
    """
    Devuelve (mock_bot, sleeps_registrados).
    - send_video_side_effect: lista de excepciones/None que devuelve send_video
      en cada llamada sucesiva.  None = éxito.
    - sleeps_registrados: lista con los segundos que se pasaron a asyncio.sleep.
    """
    sleeps = []

    async def fake_sleep(s):
        sleeps.append(s)

    # Bot.send_video como AsyncMock con side_effect controlado
    mock_bot = MagicMock()
    efectos = list(send_video_side_effect)

    async def fake_send_video(**kwargs):
        efecto = efectos.pop(0) if efectos else None
        if isinstance(efecto, Exception):
            raise efecto

    mock_bot.send_video = fake_send_video

    monkeypatch.setattr("app.services.telegram_service.Bot", lambda token: mock_bot)
    monkeypatch.setattr("asyncio.sleep", fake_sleep)
    monkeypatch.setattr(
        "app.services.telegram_service.execute_query",
        lambda sql, params=None, fetch=False: 1,
    )
    return mock_bot, sleeps


# ─── Tests ───────────────────────────────────────────────────────────────────

class TestReintentoTelegram:

    def test_envia_correctamente_al_primer_intento(self, video_fake, monkeypatch):
        """
        Sin errores: el video se envía en el primer intento y no se duerme.
        """
        _, sleeps = _mock_contexto([None], monkeypatch)   # None = éxito
        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-1"))
        assert sleeps == [], "No debe esperar si el primer intento tiene éxito"

    def test_reintenta_tras_error_de_conectividad(self, video_fake, monkeypatch):
        """
        Simula una interrupción de red en el primer intento.
        Debe reintentar y tener éxito en el segundo.
        """
        efectos = [TelegramError("Network error"), None]  # falla 1 vez, luego OK
        _, sleeps = _mock_contexto(efectos, monkeypatch)

        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-2"))

        assert len(sleeps) == 1, "Debe esperar exactamente 1 vez antes del reintento"
        assert sleeps[0] == ESPERA_BASE_S * 1, "Primera espera = ESPERA_BASE_S * 2^0"

    def test_backoff_exponencial_entre_reintentos(self, video_fake, monkeypatch):
        """
        Simula dos fallos consecutivos.
        Las esperas deben ser ESPERA_BASE_S * 1 y ESPERA_BASE_S * 2 (backoff exponencial).
        """
        efectos = [
            TelegramError("timeout"),
            TelegramError("timeout"),
            None,          # tercer intento tiene éxito
        ]
        _, sleeps = _mock_contexto(efectos, monkeypatch)

        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-3"))

        assert len(sleeps) == 2
        assert sleeps[0] == ESPERA_BASE_S * 1   # 5s
        assert sleeps[1] == ESPERA_BASE_S * 2   # 10s

    def test_agota_todos_los_reintentos_sin_propagar_excepcion(self, video_fake, monkeypatch):
        """
        Simula una interrupción total (todos los intentos fallan).
        No debe lanzar ninguna excepción al llamador.
        """
        efectos = [TelegramError("red caída")] * MAX_REINTENTOS
        _, sleeps = _mock_contexto(efectos, monkeypatch)

        # No debe lanzar — el error se maneja internamente
        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-4"))

        # Se espera entre cada par de intentos fallidos → MAX_REINTENTOS - 1 esperas
        assert len(sleeps) == MAX_REINTENTOS - 1

    def test_esperas_correctas_al_agotar_reintentos(self, video_fake, monkeypatch):
        """
        Verifica los valores exactos de backoff cuando se agotan todos los reintentos:
        5s, 10s  (para MAX_REINTENTOS = 3).
        """
        efectos = [TelegramError("sin red")] * MAX_REINTENTOS
        _, sleeps = _mock_contexto(efectos, monkeypatch)

        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-5"))

        esperados = [ESPERA_BASE_S * (2 ** i) for i in range(MAX_REINTENTOS - 1)]
        assert sleeps == esperados, f"Esperaba backoffs {esperados}, obtuvo {sleeps}"

    def test_no_reintenta_si_archivo_no_existe(self, monkeypatch):
        """
        Si el archivo de video no existe (FileNotFoundError), no se reintenta
        porque no es un error de conectividad.
        """
        sleeps = []

        async def fake_sleep(s):
            sleeps.append(s)

        mock_bot = MagicMock()
        monkeypatch.setattr("app.services.telegram_service.Bot", lambda token: mock_bot)
        monkeypatch.setattr("asyncio.sleep", fake_sleep)

        # Ruta que no existe
        _correr(_enviar_video_async("123", "/tmp/no_existe.mp4", "caption", "alerta-6"))

        assert sleeps == [], "No debe reintentar si el archivo no existe"

    def test_os_error_tambien_provoca_reintento(self, video_fake, monkeypatch):
        """
        Un OSError (p.ej. timeout de socket) también debe disparar reintentos,
        no solo TelegramError.
        """
        efectos = [OSError("connection reset"), None]
        _, sleeps = _mock_contexto(efectos, monkeypatch)

        _correr(_enviar_video_async("123", video_fake, "caption", "alerta-7"))

        assert len(sleeps) == 1, "OSError debe provocar reintento igual que TelegramError"
