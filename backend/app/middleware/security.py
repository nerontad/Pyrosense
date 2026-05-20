from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Política CSP para una API que solo devuelve JSON
CSP_API = (
    "default-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "form-action 'none'"
)


# Añade cabeceras de seguridad a cada respuesta HTTP
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Bloquea que la app sea embebida en un iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Evita que el navegador adivine el tipo MIME
        response.headers["X-Content-Type-Options"] = "nosniff"

        # No envía la URL de origen en peticiones salientes
        response.headers["Referrer-Policy"] = "no-referrer"

        # Desactiva APIs sensibles del navegador
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        )

        # Fuerza HTTPS solo si la petición ya vino por HTTPS o por un proxy HTTPS
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

        # CSP estricta excepto en archivos estáticos de video
        path = request.url.path
        if not path.startswith("/videos"):
            response.headers["Content-Security-Policy"] = CSP_API

        # No cachear respuestas dinámicas con datos de usuario
        if not path.startswith("/videos"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"

        # Quita cabeceras que revelan la tecnología del servidor
        for h in ("Server", "X-Powered-By"):
            if h in response.headers:
                del response.headers[h]

        return response
