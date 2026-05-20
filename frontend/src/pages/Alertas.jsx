import { useEffect, useState, useMemo } from 'react'
import PageShell from '../components/PageShell'
import AlertaBadge from '../components/AlertaBadge'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

// Página de historial de alertas detectadas
export default function Alertas() {
  const [alertas, setAlertas]   = useState([])
  const [cargando, setCargando] = useState(true)
  // Filtro activo: todas | pendientes | revisadas
  const [filtro, setFiltro]     = useState('todas')
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

  // Conteos para los chips del resumen
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
      title="Alertas"
      subtitle="Eventos detectados por visión artificial"
    >
      {/* Resumen */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <ResumenChip label="Total"        value={stats.total}      icon="📊" tone="zinc"/>
        <ResumenChip label="Pendientes"   value={stats.pendientes} icon="⏳" tone="amber"/>
        <ResumenChip label="Incendio"     value={stats.incendio}   icon="🔥" tone="red"/>
        <ResumenChip label="Humo"         value={stats.humo}       icon="💨" tone="orange"/>
      </section>

      {/* Filtros */}
      <div className="flex p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] mb-5 w-fit">
        {[
          { k: 'todas',      l: 'Todas' },
          { k: 'pendientes', l: `Pendientes (${stats.pendientes})` },
          { k: 'revisadas',  l: 'Revisadas' },
        ].map(f => (
          <button key={f.k} onClick={() => setFiltro(f.k)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition
                        ${filtro === f.k
                          ? 'bg-white/[0.08] text-white shadow-inner'
                          : 'text-zinc-400 hover:text-white'}`}>
            {f.l}
          </button>
        ))}
      </div>

      {cargando ? (
        <SkeletonList/>
      ) : visibles.length === 0 ? (
        <div className="panel py-16 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl
                          bg-emerald-500/15 border border-emerald-500/30 mb-4">
            <span className="text-3xl">✅</span>
          </div>
          <p className="text-white font-display text-lg font-semibold">
            {alertas.length === 0 ? 'Sin alertas registradas' : 'Sin alertas en este filtro'}
          </p>
          <p className="text-zinc-400 text-sm mt-1.5">
            {alertas.length === 0 ? 'Tu sistema está vigilando.' : 'Cambia el filtro para ver más.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {visibles.map(alerta => (
            <article key={alerta.id}
              className={`panel panel-hover p-4 sm:p-5 relative animate-fade-in-up
                          ${!alerta.revisado ? 'ring-1 ring-red-500/20' : ''}`}>
              {/* franja lateral si pendiente */}
              {!alerta.revisado && (
                <span className="absolute left-0 top-3 bottom-3 w-1 rounded-r-full
                                 bg-gradient-to-b from-red-400 to-ember-500"/>
              )}
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <AlertaBadge
                    clase={alerta.tipo_id === 1 ? 'fire' : 'smoke'}
                    confianza={alerta.confianza}
                  />
                  <div className="text-zinc-400 text-sm flex items-center gap-2">
                    <IconClock/>
                    {new Date(alerta.ocurrido_en).toLocaleString('es-CL', {
                      day: '2-digit', month: 'short',
                      hour: '2-digit', minute: '2-digit'
                    })}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {alerta.video && (
                    <a
                      href={`http://127.0.0.1:8000/videos/${alerta.video.ruta_archivo.split(/[\\/]/).pop()}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-ghost px-3 py-1.5 text-xs"
                    >
                      <IconPlay/> Ver video
                    </a>
                  )}
                  {!alerta.revisado ? (
                    <button onClick={() => marcarRevisada(alerta.id)}
                      className="btn-ghost px-3 py-1.5 text-xs">
                      <IconCheck/> Marcar revisada
                    </button>
                  ) : (
                    <span className="chip-ok">
                      <IconCheck small/> Revisada
                    </span>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </PageShell>
  )
}

function ResumenChip({ label, value, icon, tone }) {
  const tones = {
    zinc:   'from-white/[0.04] ring-white/10 text-white',
    amber:  'from-amber-500/15 ring-amber-500/20 text-amber-300',
    red:    'from-red-500/15 ring-red-500/20 text-red-300',
    orange: 'from-ember-500/15 ring-ember-500/20 text-ember-300',
  }
  return (
    <div className={`relative panel p-4 ring-1 ${tones[tone]?.split(' ').slice(1).join(' ')}`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${tones[tone]?.split(' ')[0]} to-transparent rounded-2xl pointer-events-none`}/>
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">{label}</p>
          <p className="font-display text-3xl font-bold text-white tabular-nums mt-0.5">{value}</p>
        </div>
        <span className="text-2xl opacity-80">{icon}</span>
      </div>
    </div>
  )
}

function SkeletonList() {
  return (
    <div className="space-y-3">
      {[1,2,3].map(i => (
        <div key={i} className="panel p-5">
          <div className="h-4 w-1/3 bg-white/[0.06] rounded animate-shimmer shimmer-bg"/>
          <div className="h-3 w-1/2 bg-white/[0.04] rounded mt-2 animate-shimmer shimmer-bg"/>
        </div>
      ))}
    </div>
  )
}

function IconClock() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9"/>
      <polyline points="12 7 12 12 15 14"/>
    </svg>
  )
}
function IconPlay() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="6,4 20,12 6,20"/>
    </svg>
  )
}
function IconCheck({ small }) {
  return (
    <svg width={small ? 12 : 14} height={small ? 12 : 14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  )
}
