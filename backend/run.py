# Punto de entrada del servidor backend
import os
import uvicorn

if __name__ == "__main__":
    # Obtener puerto de variables de entorno, por defecto 8000
    port = int(os.environ.get("PORT", 8000))
    # Iniciar servidor Uvicorn con la app FastAPI
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)