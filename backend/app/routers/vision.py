import os
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.vision_service import vision
from app.routers.auth import get_current_user

router = APIRouter(prefix="/vision", tags=["Visión"])

# Bearer opcional: permite que el endpoint funcione sin token en modo local
_bearer_opcional = HTTPBearer(auto_error=False)


# Modo de demostración local: si VISION_PUBLIC está activo, no exige login.
# En producción se deja sin definir, por lo que el endpoint requiere autenticación.
def _modo_publico() -> bool:
    return os.getenv("VISION_PUBLIC", "").lower() in ("1", "true", "yes", "si")


# Autenticación normal por defecto; en modo local permite probar la demo sin login.
def usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(_bearer_opcional)):
    if _modo_publico():
        return {"id": "demo-local"}
    if credentials is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    return get_current_user(credentials)


# Non-Max Suppression: elimina cajas duplicadas que se solapan
def _nms(detecciones: list, iou_thr: float = 0.45) -> list:
    if not detecciones:
        return []
    cajas = []
    for d in detecciones:
        cx, cy, w, h = d["bbox"]
        cajas.append([cx - w / 2, cy - h / 2, w, h])  # x,y,w,h (esquina sup. izq.)
    confs = [d["confianza"] for d in detecciones]
    indices = cv2.dnn.NMSBoxes(cajas, confs, score_threshold=0.0, nms_threshold=iou_thr)
    if len(indices) == 0:
        return []
    return [detecciones[i] for i in np.array(indices).flatten()]


# Recibe un frame (imagen JPEG/PNG) desde la cámara del navegador y devuelve
# las detecciones de fuego/humo con coordenadas relativas (0..1) para dibujarlas.
@router.post("/detectar")
async def detectar(imagen: UploadFile = File(...), usuario=Depends(usuario_actual)):
    if not vision.modelo_cargado():
        raise HTTPException(status_code=503, detail="Modelo de detección no disponible")

    contenido = await imagen.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="Imagen vacía")

    buffer = np.frombuffer(contenido, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")

    detecciones = _nms(vision.inferir(frame))

    # inferir() devuelve cajas (cx, cy, w, h) en píxeles de la imagen original.
    # Las normalizamos a 0..1 para que el frontend las escale a cualquier tamaño.
    alto, ancho = frame.shape[:2]
    resultado = []
    for d in detecciones:
        cx, cy, w, h = d["bbox"]
        resultado.append({
            "clase": d["clase"],
            "confianza": d["confianza"],
            "x": max(0.0, (cx - w / 2) / ancho),
            "y": max(0.0, (cy - h / 2) / alto),
            "w": w / ancho,
            "h": h / alto,
        })

    return {"detecciones": resultado}


# Página de demostración local independiente (sin React ni login).
# Solo disponible cuando VISION_PUBLIC está activo. Sirve para probar rápido
# la cámara del dispositivo + detección desde http://localhost:8000/vision/demo
@router.get("/demo", response_class=HTMLResponse)
def demo_page():
    if not _modo_publico():
        raise HTTPException(status_code=404, detail="No disponible")
    return HTMLResponse(_DEMO_HTML)


_DEMO_HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Demo cámara - Deteccion de fuego/humo</title>
<style>
 body{margin:0;background:#0a0a0a;color:#eee;font-family:system-ui,sans-serif;text-align:center}
 h1{font-size:18px;margin:16px}
 #wrap{position:relative;display:inline-block;max-width:100%;padding:0 8px}
 canvas{max-width:100%;background:#000;border-radius:10px}
 button{background:#ea580c;color:#fff;border:0;padding:10px 16px;border-radius:8px;font-size:15px;margin:6px;cursor:pointer}
 button.sec{background:#333}
 #estado{margin:10px;font-weight:bold;min-height:20px}
 video{display:none}
</style>
</head>
<body>
 <h1>🔥 Demo local - camara del dispositivo</h1>
 <div>
   <button id="start">▶ Iniciar</button>
   <button id="stop" class="sec">■ Detener</button>
   <button id="flip" class="sec">🔄 Cambiar camara</button>
 </div>
 <div id="estado">Pulsa Iniciar y permite el acceso a la camara</div>
 <div id="wrap"><canvas id="canvas"></canvas></div>
 <video id="video" muted playsinline></video>
<script>
const video=document.getElementById('video'),canvas=document.getElementById('canvas'),
      ctx=canvas.getContext('2d'),estado=document.getElementById('estado');
let stream=null,raf=null,timer=null,enviando=false,dets=[],facing='environment';
async function start(){
  try{
    stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:facing}},audio:false});
    video.srcObject=stream; await video.play(); estado.textContent='Analizando...'; render(); loop();
  }catch(e){ estado.textContent='Error al abrir la camara: '+e.message; }
}
function stop(){
  if(timer)clearTimeout(timer); if(raf)cancelAnimationFrame(raf);
  if(stream)stream.getTracks().forEach(t=>t.stop()); stream=null; dets=[]; estado.textContent='Detenido';
}
function flip(){ facing=facing==='environment'?'user':'environment'; if(stream){stop();setTimeout(start,200);} }
function render(){
  const draw=()=>{
    if(video.videoWidth){
      if(canvas.width!==video.videoWidth){canvas.width=video.videoWidth;canvas.height=video.videoHeight;}
      ctx.drawImage(video,0,0,canvas.width,canvas.height);
      for(const d of dets){
        const x=d.x*canvas.width,y=d.y*canvas.height,w=d.w*canvas.width,h=d.h*canvas.height;
        const c=d.clase==='fire'?'#ef4444':'#f59e0b';
        ctx.lineWidth=Math.max(2,canvas.width/320); ctx.strokeStyle=c; ctx.strokeRect(x,y,w,h);
        const t=d.clase+' '+Math.round(d.confianza*100)+'%';
        ctx.font=Math.max(14,canvas.width/40)+'px sans-serif';
        const tw=ctx.measureText(t).width,th=Math.max(18,canvas.width/30);
        ctx.fillStyle=c; ctx.fillRect(x,Math.max(0,y-th),tw+10,th);
        ctx.fillStyle='#fff'; ctx.fillText(t,x+5,Math.max(th-5,y-5));
      }
    }
    raf=requestAnimationFrame(draw);
  }; draw();
}
function loop(){
  const tick=async()=>{
    if(video.videoWidth && !enviando){
      enviando=true;
      try{
        const s=Math.min(1,480/video.videoWidth);
        const off=document.createElement('canvas');
        off.width=Math.round(video.videoWidth*s); off.height=Math.round(video.videoHeight*s);
        off.getContext('2d').drawImage(video,0,0,off.width,off.height);
        const blob=await new Promise(r=>off.toBlob(r,'image/jpeg',0.6));
        const fd=new FormData(); fd.append('imagen',blob,'f.jpg');
        const r=await fetch('/vision/detectar',{method:'POST',body:fd});
        const j=await r.json(); dets=j.detecciones||[];
        const fuego=dets.some(d=>d.clase==='fire');
        estado.textContent=fuego?('🔥 FUEGO DETECTADO ('+dets.length+')'):('Analizando... ('+dets.length+' detecciones)');
      }catch(e){/*reintenta en el proximo tick*/}
      finally{enviando=false;}
    }
    timer=setTimeout(tick,700);
  }; tick();
}
document.getElementById('start').onclick=start;
document.getElementById('stop').onclick=stop;
document.getElementById('flip').onclick=flip;
</script>
</body>
</html>"""
