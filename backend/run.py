import os
import uvicorn

# Entrada principal del backend
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        # No envía cabeceras Server ni Date (oculta versión del stack)
        server_header=False,
        date_header=False,
        # Respeta X-Forwarded-Proto si está detrás de un proxy
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
