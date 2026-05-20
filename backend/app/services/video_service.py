import subprocess
import os
from datetime import datetime
from app.config import get_settings
from app.database.connection import execute_one

settings = get_settings()

# Graba un clip MP4 desde el stream RTSP de la cámara
def grabar_clip(camara_id: str) -> dict | None:
    os.makedirs(settings.video_output_dir, exist_ok=True)

    # Obtiene la URL RTSP original de la cámara
    camara = execute_one(
        "SELECT url_rtsp FROM camaras WHERE id = %s",
        (camara_id,)
    )
    if not camara:
        print(f"Cámara {camara_id} no encontrada en BD")
        return None

    url_rtsp = camara["url_rtsp"]
    duracion_seg = settings.buffer_seconds
    # Nombre con timestamp para no sobrescribir
    nombre_archivo = f"alerta_{camara_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    ruta = os.path.join(settings.video_output_dir, nombre_archivo)

    print(f"Grabando clip con ffmpeg: {url_rtsp}")

    try:
        # Ejecuta ffmpeg para grabar N segundos del stream
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", url_rtsp,
            "-t", str(duracion_seg),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-y",
            ruta
        ]
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duracion_seg + 30
        )

        if resultado.returncode != 0:
            print(f"ffmpeg error: {resultado.stderr[-500:]}")
            return None

        if not os.path.exists(ruta):
            print("ffmpeg no generó el archivo de salida")
            return None

        # Devuelve los metadatos del clip generado
        tamano = os.path.getsize(ruta)
        print(f"Clip grabado: {ruta} ({duracion_seg}s, {tamano} bytes)")
        return {
            "ruta_archivo": ruta,
            "duracion_seg": duracion_seg,
            "tamano_bytes": tamano
        }

    except subprocess.TimeoutExpired:
        print("ffmpeg timeout al grabar clip")
        return None
    except FileNotFoundError:
        print("ffmpeg no encontrado — instálalo desde https://ffmpeg.org/download.html")
        return None
    except Exception as e:
        print(f"Error al grabar clip: {e}")
        return None
