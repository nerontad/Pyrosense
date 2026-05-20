import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../components/PageShell'
import SensorCard from '../components/SensorCard'
import GraficoSensor from '../components/GraficoSensor'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

// Vista principal: KPIs, sensores en vivo y gráfico por dispositivo
export default function Dashboard() {
  const [dispositivos, setDispositivos] = useState([])
  const [lecturas, setLecturas] = useState({})
  const [alertasRecientes, setAlertasRecientes] = useState([])
  // WebSocket que recibe lecturas en tiempo real
  const { datos, conectado } = useWebSocket('/ws/sensores')

  // Carga inicial de dispositivos y últimas alertas
  useEffect(() => {
    api.get('/dispositivos/').then(res => setDispositivos(res.data)).catch(() => {})
    api.get('/alertas/?limite=5').then(res => setAlertasRecientes(res.data)).catch(() => {})
  }, [])

  // Aplica las lecturas recibidas por WS sobre el estado
  useEffect(() => {
    if (!datos) return
    if (datos.tipo === 'lecturas_iniciales') {
      setLecturas(datos.datos)
    } else if (datos.dispositivo_id) {
      setLecturas(prev => ({ ...prev, [datos.dispositivo_id]: datos }))
    }
  }, [datos])

  // Métricas agregadas mostradas en la cabecera
  const stats = calcularStats(dispositivos, lecturas, alertasRecientes)

  return (
    <PageShell
      title="Dashboard"
      subtitle="Vista general en tiempo real de tu red de detección"
      actions={(
        <span className={`chip ${conectado ? 'chip-ok' : 'chip-mute'} px-3 py-1.5`}>
          <span className={`w-2 h-2 rounded-full ${conectado ? 'bg-emerald-400 animate-pulse-soft' : 'bg-zinc-500'}`}/>
          {conectado ? 'En vivo' : 'Desconectado'}
        </span>
      )}
    >
      {/* KPI strip */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <KpiCard
          label="Dispositivos"
          value={stats.total}
          hint={`${stats.activos} activos`}
          icon="📡"
          color="ember"
        />
        <KpiCard
          label="Temp. promedio"
          value={stats.tempProm !== null ? `${stats.tempProm.toFixed(1)}°` : '—'}
          hint="Última muestra"
          icon="🌡️"
          color="ember"
        />
        <KpiCard
          label="Humedad prom."
          value={stats.humProm !== null ? `${stats.humProm.toFixed(0)}%` : '—'}
          hint="Última muestra"
          icon="💧"
          color="sky"
        />
        <KpiCard
          label="Alertas (24h)"
          value={stats.alertas24h}
          hint={stats.alertas24h > 0 ? 'Revisar pendientes' : 'Sin novedades'}
          icon="🚨"
          color={stats.alertas24h > 0 ? 'red' : 'emerald'}
        />
      </section>

      {/* Empty state */}
      {dispositivos.length === 0 ? (
        <EmptyState/>
      ) : (
        <div className="space-y-10">
          {dispositivos.map(disp => {
            const lectura = lecturas[disp.id]
            const tieneDatos = !!lectura
            return (
              <section key={disp.id} className="animate-fade-in-up">
                <header className="flex items-center justify-between flex-wrap gap-3 mb-4">
                  <div className="flex items-center gap-3">
                    <span className="relative flex h-9 w-9 items-center justify-center rounded-xl
                                     bg-gradient-to-br from-ember-500/20 to-red-500/10
                                     border border-ember-500/30">
                      <span className="text-lg">📡</span>
                    </span>
                    <div>
                      <h2 className="text-white font-display font-semibold tracking-tight">
                        {disp.nombre}
                      </h2>
                      <p className="text-xs text-zinc-500 font-mono">{disp.id}</p>
                    </div>
                  </div>
                  <span className={`chip ${tieneDatos ? 'chip-ok' : 'chip-mute'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${tieneDatos ? 'bg-emerald-400 animate-pulse-soft' : 'bg-zinc-500'}`}/>
                    {tieneDatos ? 'Recibiendo datos' : 'Sin datos'}
                  </span>
                </header>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                  <SensorCard
                    titulo="Temperatura"
                    valor={lectura?.temperatura}
                    unidad="°C"
                    icono="🌡️"
                    color="naranja"
                  />
                  <SensorCard
                    titulo="Humedad"
                    valor={lectura?.humedad}
                    unidad="%"
                    icono="💧"
                    color="azul"
                  />
                  <SensorCard
                    titulo="CO₂"
                    valor={lectura?.co2_ppm}
                    unidad="ppm"
                    icono="💨"
                    color="verde"
                  />
                </div>

                <GraficoSensor dispositivoId={disp.id} />
              </section>
            )
          })}
        </div>
      )}
    </PageShell>
  )
}

// Tarjeta de indicador (KPI) con color y glow
function KpiCard({ label, value, hint, icon, color = 'ember' }) {
  const colors = {
    ember:   { glow: 'from-ember-500/20',   text: 'text-ember-300',   ring: 'ring-ember-500/20' },
    sky:     { glow: 'from-sky-500/20',     text: 'text-sky-300',     ring: 'ring-sky-500/20' },
    emerald: { glow: 'from-emerald-500/20', text: 'text-emerald-300', ring: 'ring-emerald-500/20' },
    red:     { glow: 'from-red-500/25',     text: 'text-red-300',     ring: 'ring-red-500/20' },
  }
  const c = colors[color] || colors.ember
  return (
    <div className={`relative panel panel-hover overflow-hidden p-4 sm:p-5 ring-1 ${c.ring}`}>
      <div className={`pointer-events-none absolute -top-12 -right-12 w-32 h-32 rounded-full
                       bg-gradient-to-br ${c.glow} to-transparent blur-2xl`}/>
      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-medium">{label}</p>
          <p className="font-display text-2xl sm:text-3xl font-bold text-white mt-1.5 tabular-nums">
            {value}
          </p>
          <p className={`text-[11px] mt-1 ${c.text}`}>{hint}</p>
        </div>
        <span className="text-2xl opacity-80">{icon}</span>
      </div>
    </div>
  )
}

// Estado vacío cuando no hay dispositivos registrados
function EmptyState() {
  return (
    <div className="panel py-16 text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl
                      bg-gradient-to-br from-ember-500/20 to-red-500/10
                      border border-ember-500/30 mb-4">
        <span className="text-3xl">📡</span>
      </div>
      <h3 className="text-white font-display text-lg font-semibold">
        No hay dispositivos IoT registrados
      </h3>
      <p className="text-zinc-400 text-sm mt-1.5 max-w-sm mx-auto">
        Agrega tu primer dispositivo para empezar a recibir lecturas en tiempo real.
      </p>
      <Link to="/dispositivos" className="btn-ember mt-5">
        + Agregar dispositivo
      </Link>
    </div>
  )
}

// Calcula promedios y conteos para mostrar en KPIs
function calcularStats(dispositivos, lecturas, alertas) {
  const total = dispositivos.length
  const ls = Object.values(lecturas).filter(l => l && typeof l === 'object')
  const activos = ls.length
  const promedio = (key) => {
    const arr = ls.map(l => l[key]).filter(v => v != null && !isNaN(v))
    if (arr.length === 0) return null
    return arr.reduce((a, b) => a + Number(b), 0) / arr.length
  }
  const ahora = Date.now()
  const alertas24h = alertas.filter(a => {
    const t = new Date(a.ocurrido_en).getTime()
    return ahora - t < 24 * 3600 * 1000
  }).length
  return {
    total,
    activos,
    tempProm: promedio('temperatura'),
    humProm:  promedio('humedad'),
    alertas24h,
  }
}
