import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'

// Reproductor de stream HLS de cámara con indicador de señal
export default function VideoPlayer({ urlHls }) {
  const videoRef = useRef(null)
  // Estado del stream: cargando | live | error
  const [estado, setEstado] = useState('cargando')

  // Inicializa HLS y maneja eventos del reproductor
  useEffect(() => {
    const video = videoRef.current
    if (!video || !urlHls) return
    setEstado('cargando')

    let hls
    if (Hls.isSupported()) {
      hls = new Hls()
      hls.loadSource(urlHls)
      hls.attachMedia(video)
      hls.on(Hls.Events.MANIFEST_PARSED, () => setEstado('live'))
      hls.on(Hls.Events.ERROR, (_, data) => { if (data.fatal) setEstado('error') })
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = urlHls
      video.addEventListener('loadedmetadata', () => setEstado('live'))
      video.addEventListener('error', () => setEstado('error'))
    }
    return () => { hls && hls.destroy() }
  }, [urlHls])

  return (
    <div className="relative bg-char-950 aspect-video overflow-hidden">
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        controls
        muted
        playsInline
      />

      {/* Indicador de señal */}
      <div className="pointer-events-none absolute top-3 left-3">
        {estado === 'live' ? (
          <span className="flex items-center gap-2 bg-fire-grad text-char-950 shadow-ember-glow
                           px-2 py-1 font-mono text-[13px] font-semibold tracking-[0.2em] uppercase">
            <span className="dot bg-char-950 animate-blink"/>
            Rec — Vivo
          </span>
        ) : (
          <span className="flex items-center gap-2 bg-char-950/80 border border-line text-ash-300
                           px-2 py-1 font-mono text-[13px] tracking-[0.2em] uppercase">
            {estado === 'error' ? 'Sin señal' : 'Conectando'}
          </span>
        )}
      </div>

      {/* Estado de error */}
      {estado === 'error' && (
        <div className="absolute inset-0 flex flex-col items-start justify-end p-6 bg-char-950/70">
          <p className="font-display type-expanded font-bold uppercase text-bone text-lg">
            Sin señal
          </p>
          <p className="font-mono text-[13px] text-ash-400 mt-1 tracking-wide">
            // El stream no está disponible
          </p>
        </div>
      )}
      {estado === 'cargando' && (
        <div className="absolute inset-0 flex items-center justify-center bg-char-950/60">
          <span className="font-mono text-[13px] uppercase tracking-[0.3em] text-ash-400 animate-blink">
            Estableciendo enlace…
          </span>
        </div>
      )}
    </div>
  )
}
