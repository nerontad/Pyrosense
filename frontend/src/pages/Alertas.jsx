import { useEffect, useState, useMemo } from 'react'
import PageShell from '../components/PageShell'
import AlertaBadge from '../components/AlertaBadge'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

// Construye la URL pública del video usando el mismo host del API
function urlVideoAlerta(rutaArchivo) {
  if (!rutaArchivo) return null
  const archivo = rutaArchivo.split(/[\\/]/).pop()
  return `${api.defaults.baseURL}/videos/${archivo}`
}

// Página de historial de alertas detectadas
export default function Alertas() {
  const [alertas, setAlertas]   = useState([])
  const [cargando, setCargando] = useState(true)
  // Filtro activo: todas | pendientes | revisadas
  const [filtro, setFiltro]     = useState('todas')
  // Alerta cuyo video se está visualizando en el modal
  const [verVideo, setVerVideo] = useState(null)
  // WebSocket que avisa cuando se genera una nueva alerta
  const { datos } = useWebSocket('/ws/alertas')

  // Carga inicial del historial
  useEffect(() => {
    api.get('/alertas/?limite=30')
      .then(res => setAlertas(res.data))
      .finally(() => setCargando(false))
  }, [])

  // Refresca la lista cuando llega una alerta nueva por WS
  useEffect(() => {
    if (datos?.tipo === 'nueva_alerta') {
      api.get('/alertas/?limite=30').then(res => setAlertas(res.data))
    }
  }, [datos])

  // Conteos para la franja de resumen
  const stats = useMemo(() => {
    const total = alertas.length
    const pendientes = alertas.filter(a => !a.revisado).length
    const incendio   = alertas.filter(a => a.tipo_id === 1).length
    const humo       = alertas.filter(a => a.tipo_id !== 1).length
    return { total, pendientes, incendio, humo }
  }, [alertas])

  // Alertas filtradas según el filtro activo
  const visibles = alertas.filter(a => {
    if (filtro === 'pendientes') return !a.revisado
    if (filtro === 'revisadas')  return a.revisado
    return true
  })

  // Marca la alerta como revisada en el backend y en el estado local
  const marcarRevisada = async (id) => {
    await api.patch(`/alertas/${id}/revisar`)
    setAlertas(prev => prev.map(a => a.id === id ? { ...a, revisado: true } : a))
  }

  return (
    <PageShell
      index="03"
      title="Alertas"
      subtitle="Eventos detectados por visión artificial"
    >
      {/* Franja de resumen con hairlines internas y acento por categoría */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-line border border-line mb-12 stagger">
        <StatCell label="Total registradas" value={stats.total} tone="bone"/>
        <StatCell label="Pendientes" value={stats.pendientes}
                  tone={stats.pendientes > 0 ? 'ember' : 'mute'} pulso={stats.pendientes > 0}/>
        <StatCell label="Incendio" value={stats.incendio} tone={stats.incendio > 0 ? 'ember' : 'mute'}/>
        <StatCell label="Humo" value={stats.humo} tone={stats.humo > 0 ? 'flare' : 'mute'}/>
      </section>

      {/* Filtros: tabs con subrayado */}
      <div className="flex gap-1 border-b border-line mb-10">
        {[
          { k: 'todas',      l: 'Todas' },
          { k: 'pendientes', l: `Pendientes (${stats.pendientes})` },
          { k: 'revisadas',  l: 'Revisadas' },
        ].map(f => (
          <button key={f.k} onClick={() => setFiltro(f.k)}
            className={`px-4 pb-3 -mb-px font-mono text-[11px] uppercase tracking-[0.18em]
                        border-b-2 transition-colors duration-200
                        ${filtro === f.k
                          ? 'text-bone border-ember-500'
                          : 'text-ash-500 border-transparent hover:text-bone'}`}>
            {f.l}
          </button>
        ))}
      </div>

      {cargando ? (
        <SkeletonList/>
      ) : visibles.length === 0 ? (
        <div className="relative border border-line p-8 sm:p-14 overflow-hidden">
          <div className="absolute inset-0 bg-moss-wash pointer-events-none"/>
          <p className="kicker relative">{alertas.length === 0 ? 'Registro limpio' : 'Filtro sin resultados'}</p>
          <h3 className="relative font-display type-expanded font-black uppercase text-bone
                         text-[clamp(1.5rem,3.4vw,2.4rem)] mt-5 max-w-lg leading-tight">
            {alertas.length === 0
              ? <>Sin eventos <span className="text-moss-300">detectados</span></>
              : 'Nada bajo este filtro'}
          </h3>
          <p className="relative font-mono text-[13px] text-ash-300 mt-5 leading-relaxed">
            {alertas.length === 0
              ? '// El sistema está vigilando. Las detecciones aparecerán aquí.'
              : '// Cambia el filtro para ver más eventos.'}
          </p>
        </div>
      ) : (
        // Libro mayor de eventos: filas con hairlines
        <div className="border border-line divide-y divide-line stagger">
          {visibles.map(alerta => {
            const fecha = new Date(alerta.ocurrido_en)
            return (
              <article key={alerta.id}
                className="group relative grid grid-cols-12 items-center gap-x-4 gap-y-3
                           px-5 sm:px-6 py-5 bg-char-850 hover:bg-char-800
                           transition-colors duration-200">
                {/* Franja brasa si está pendiente */}
                {!alerta.revisado && (
                  <span className="absolute left-0 top-0 bottom-0 w-[3px] bg-ember-500
                                   shadow-[2px_0_14px_rgba(255,77,0,0.45)]"/>
                )}

                {/* Timestamp */}
                <div className="col-span-6 sm:col-span-3 font-mono tabular-nums">
                  <p className="text-bone text-sm">
                    {fecha.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  <p className="text-ash-500 text-[11px] uppercase tracking-[0.15em] mt-0.5">
                    {fecha.toLocaleDateString('es-CL', { day: '2-digit', month: 'short' })}
                  </p>
                </div>

                {/* Tipo + confianza */}
                <div className="col-span-6 sm:col-span-4">
                  <AlertaBadge
                    clase={alerta.tipo_id === 1 ? 'fire' : 'smoke'}
                    confianza={alerta.confianza}
                  />
                </div>

                {/* Acciones */}
                <div className="col-span-12 sm:col-span-5 flex items-center sm:justify-end gap-5">
                  {alerta.video && (
                    <button onClick={() => setVerVideo(alerta)}
                      className="btn-bare link-grow text-bone">
                      Ver video →
                    </button>
                  )}
                  {!alerta.revisado ? (
                    <button onClick={() => marcarRevisada(alerta.id)}
                      className="btn-bare link-grow hover:text-moss-300">
                      Marcar revisada
                    </button>
                  ) : (
                    <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-moss-300">
                      ✓ Revisada
                    </span>
                  )}
                </div>
              </article>
            )
          })}
        </div>
      )}

      {/* Modal reproductor de video */}
      {verVideo && (
        <VideoModal
          alerta={verVideo}
          onClose={() => setVerVideo(null)}
        />
      )}
    </PageShell>
  )
}

// Modal con player de video para la alerta seleccionada
function VideoModal({ alerta, onClose }) {
  const src = urlVideoAlerta(alerta.video?.ruta_archivo)
  const esIncendio = alerta.tipo_id === 1

  // Cierre con tecla Escape
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center
                 bg-char-950/85 p-4 animate-fade-up"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative bg-char-850 border border-line max-w-3xl w-full"
      >
        <div className="absolute inset-x-0 top-0 h-[3px] bg-ember-500"/>

        <div className="flex items-start justify-between gap-4 px-6 py-5 border-b border-line">
          <div>
            <h3 className="font-display type-expanded font-bold uppercase tracking-wide
                           text-bone text-lg">
              {esIncendio ? 'Incendio detectado' : 'Humo detectado'}
            </h3>
            <p className="font-mono text-[12px] text-ash-400 mt-2 tracking-wide">
              {new Date(alerta.ocurrido_en).toLocaleString('es-CL', {
                day: '2-digit', month: 'long', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
              })}
              {alerta.confianza != null && (
                <> · Confianza {(alerta.confianza * 100).toFixed(0)}%</>
              )}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-ash-400 hover:text-ember-400 transition-colors"
            aria-label="Cerrar"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
                 width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="p-6">
          {src ? (
            <video
              src={src}
              controls
              autoPlay
              className="w-full bg-char-950 aspect-video"
            />
          ) : (
            <div className="font-mono text-[13px] text-ash-300 py-12 text-center">
              // No hay video disponible para esta alerta
            </div>
          )}

          {alerta.video?.ruta_archivo && (
            <p className="font-mono text-[11px] text-ash-500 mt-4 truncate">
              {alerta.video.ruta_archivo}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// Celda de la franja de resumen, con regla superior en el color de su categoría
function StatCell({ label, value, tone = 'mute', pulso = false }) {
  const tones = {
    bone:  { bar: 'bg-bone/40',     num: 'text-bone' },
    ember: { bar: 'bg-ember-500',   num: 'text-ember-400' },
    flare: { bar: 'bg-flare-400',   num: 'text-flare-300' },
    mute:  { bar: 'bg-ash-600/40',  num: 'text-ash-400' },
  }
  const t = tones[tone] || tones.mute
  return (
    <div className="relative bg-char-850 px-5 py-6 sm:px-7 transition-colors duration-200 hover:bg-char-800">
      <span className={`absolute top-0 left-0 w-10 h-[3px] ${t.bar} ${pulso ? 'animate-blink' : ''}`}/>
      <p className="kicker">{label}</p>
      <p className={`num-display text-3xl sm:text-4xl mt-3 ${t.num} ${pulso ? 'glow-ember' : ''}`}>
        {value}
      </p>
    </div>
  )
}

function SkeletonList() {
  return (
    <div className="border border-line divide-y divide-line">
      {[1, 2, 3].map(i => (
        <div key={i} className="bg-char-850 px-6 py-5">
          <div className="h-4 w-1/3 shimmer-bg animate-shimmer"/>
          <div className="h-3 w-1/2 mt-2 shimmer-bg animate-shimmer"/>
        </div>
      ))}
    </div>
  )
}
