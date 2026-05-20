import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'

// Reproductor de stream HLS de cámara con overlay de estado
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
    <div className="relative bg-black aspect-video overflow-hidden">
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        controls
        muted
        playsInline
      />

      {/* Indicador de estado en la esquina */}
      <div className="pointer-events-none absolute top-3 left-3 flex items-center gap-2">
        <span className={`px-2 py-1 rounded-md text-[10px] font-bold tracking-wider
                          backdrop-blur-md flex items-center gap-1.5
                          ${estado === 'live'
                            ? 'bg-red-600/80 text-white'
                            : estado === 'error'
                              ? 'bg-zinc-700/80 text-zinc-300'
                              : 'bg-black/60 text-zinc-300'}`}>
          {estado === 'live' && <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse-soft"/>}
          {estado === 'live' ? 'LIVE' : estado === 'error' ? 'OFFLINE' : 'CARGANDO'}
        </span>
      </div>

      {/* Estado vacío / error */}
      {estado === 'error' && (
        <div className="absolute inset-0 flex flex-col items-center justify-center
                        bg-gradient-to-b from-black/40 to-black/80 text-zinc-300">
          <span className="text-3xl mb-2">📡</span>
          <p className="text-sm font-medium">Sin señal</p>
          <p className="text-xs text-zinc-500">El stream no está disponible</p>
        </div>
      )}
      {estado === 'cargando' && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/40">
          <span className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
        </div>
      )}
    </div>
  )
}
