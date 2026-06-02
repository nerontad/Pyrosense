import { useEffect, useRef, useState } from 'react'
import api from '../services/api'

// Cada cuántos ms se envía un frame al backend para detectar (auto-ajustado:
// nunca se envía un frame nuevo hasta que vuelve la respuesta del anterior).
const INTERVALO_MS = 700
// Ancho máximo del frame que se manda al backend (menos peso = más rápido).
const ANCHO_ENVIO = 480

// Demo: usa la cámara del notebook/celular y dibuja en vivo las detecciones
// de fuego/humo que devuelve el modelo YOLO del backend.
export default function DetectorLocal() {
  const videoRef    = useRef(null)   // <video> oculto: fuente de la cámara
  const canvasRef   = useRef(null)   // <canvas> visible: video + cajas
  const enviandoRef = useRef(false)  // evita solapar peticiones al backend
  const deteccionesRef = useRef([])  // últimas detecciones (las dibuja el rAF)
  const streamRef   = useRef(null)
  const rafRef      = useRef(null)
  const timerRef    = useRef(null)

  const [activo, setActivo]       = useState(false)
  const [error, setError]         = useState('')
  const [facingMode, setFacing]   = useState('environment') // 'environment'=trasera
  const [detecciones, setDet]     = useState([])

  // Arranca la cámara y los bucles de render + detección
  const iniciar = async () => {
    setError('')
    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Tu navegador no permite acceder a la cámara (se requiere HTTPS).')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: facingMode } },
        audio: false,
      })
      streamRef.current = stream
      const video = videoRef.current
      video.srcObject = stream
      await video.play()
      setActivo(true)
      bucleRender()
      bucleDeteccion()
    } catch (e) {
      if (e.name === 'NotAllowedError')      setError('Permiso de cámara denegado.')
      else if (e.name === 'NotFoundError')   setError('No se encontró ninguna cámara.')
      else                                   setError('No se pudo abrir la cámara: ' + e.message)
    }
  }

  // Detiene la cámara y limpia los bucles
  const detener = () => {
    setActivo(false)
    if (timerRef.current) clearTimeout(timerRef.current)
    if (rafRef.current)   cancelAnimationFrame(rafRef.current)
    streamRef.current?.getTracks().forEach(t => t.stop())
    streamRef.current = null
    deteccionesRef.current = []
    setDet([])
  }

  // Cambia entre cámara frontal y trasera (reabre el stream)
  const cambiarCamara = () => {
    const nuevo = facingMode === 'environment' ? 'user' : 'environment'
    setFacing(nuevo)
    if (activo) { detener(); setTimeout(iniciar, 200) }
  }

  // Dibuja el video y las cajas de detección en el canvas (60 fps aprox.)
  const bucleRender = () => {
    const video  = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return
    const ctx = canvas.getContext('2d')

    const dibujar = () => {
      if (video.videoWidth) {
        if (canvas.width !== video.videoWidth) {
          canvas.width  = video.videoWidth
          canvas.height = video.videoHeight
        }
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        for (const d of deteccionesRef.current) {
          const x = d.x * canvas.width
          const y = d.y * canvas.height
          const w = d.w * canvas.width
          const h = d.h * canvas.height
          const color = d.clase === 'fire' ? '#ef4444' : '#f59e0b'

          ctx.lineWidth = Math.max(2, canvas.width / 320)
          ctx.strokeStyle = color
          ctx.strokeRect(x, y, w, h)

          const etiqueta = `${d.clase} ${Math.round(d.confianza * 100)}%`
          ctx.font = `${Math.max(14, canvas.width / 40)}px sans-serif`
          const tw = ctx.measureText(etiqueta).width
          const th = Math.max(18, canvas.width / 30)
          ctx.fillStyle = color
          ctx.fillRect(x, Math.max(0, y - th), tw + 10, th)
          ctx.fillStyle = '#fff'
          ctx.fillText(etiqueta, x + 5, Math.max(th - 5, y - 5))
        }
      }
      rafRef.current = requestAnimationFrame(dibujar)
    }
    dibujar()
  }

  // Captura un frame, lo envía al backend y guarda las detecciones recibidas
  const bucleDeteccion = () => {
    const tick = async () => {
      const video = videoRef.current
      if (video?.videoWidth && !enviandoRef.current) {
        enviandoRef.current = true
        try {
          const escala  = Math.min(1, ANCHO_ENVIO / video.videoWidth)
          const off     = document.createElement('canvas')
          off.width     = Math.round(video.videoWidth * escala)
          off.height    = Math.round(video.videoHeight * escala)
          off.getContext('2d').drawImage(video, 0, 0, off.width, off.height)

          const blob = await new Promise(r => off.toBlob(r, 'image/jpeg', 0.6))
          const form = new FormData()
          form.append('imagen', blob, 'frame.jpg')

          const { data } = await api.post('/vision/detectar', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
          deteccionesRef.current = data.detecciones || []
          setDet(deteccionesRef.current)
        } catch {
          /* ignora errores puntuales de red/frame y reintenta en el próximo tick */
        } finally {
          enviandoRef.current = false
        }
      }
      timerRef.current = setTimeout(tick, INTERVALO_MS)
    }
    tick()
  }

  // Limpia todo al desmontar el componente
  useEffect(() => () => detener(), [])

  const hayFuego = detecciones.some(d => d.clase === 'fire')

  return (
    <div className="panel overflow-hidden">
      <div className="relative bg-black aspect-video">
        <video ref={videoRef} className="hidden" muted playsInline />
        <canvas ref={canvasRef} className="w-full h-full object-contain" />

        {!activo && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-300">
            <span className="text-3xl mb-2">🎥</span>
            <p className="text-sm font-medium">Cámara del dispositivo</p>
            <p className="text-xs text-zinc-500">Inicia la demo para detectar fuego/humo en vivo</p>
          </div>
        )}

        {activo && (
          <div className="pointer-events-none absolute top-3 left-3">
            <span className={`px-2 py-1 rounded-md text-[10px] font-bold tracking-wider
                              backdrop-blur-md flex items-center gap-1.5
                              ${hayFuego ? 'bg-red-600/90 text-white' : 'bg-emerald-600/80 text-white'}`}>
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse-soft"/>
              {hayFuego ? '🔥 FUEGO DETECTADO' : 'ANALIZANDO'}
            </span>
          </div>
        )}
      </div>

      <div className="p-4 sm:p-5 flex flex-wrap items-center gap-2">
        {!activo ? (
          <button onClick={iniciar} className="btn-ember">▶ Iniciar demo</button>
        ) : (
          <button onClick={detener} className="btn-ghost">■ Detener</button>
        )}
        <button onClick={cambiarCamara} className="btn-ghost">
          🔄 {facingMode === 'environment' ? 'Usar frontal' : 'Usar trasera'}
        </button>
        {activo && (
          <span className="text-xs text-zinc-500 ml-auto">
            {detecciones.length} detección(es)
          </span>
        )}
        {error && <p className="w-full text-red-400 text-sm">{error}</p>}
      </div>
    </div>
  )
}
