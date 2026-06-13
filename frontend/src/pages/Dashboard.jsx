import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageShell from '../components/PageShell'
import SensorCard from '../components/SensorCard'
import GraficoSensor from '../components/GraficoSensor'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

// Vista principal: estado general del sistema, telemetría en vivo y gráfico por dispositivo
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

  // Métricas agregadas mostradas en el módulo de estado
  const stats = calcularStats(dispositivos, lecturas, alertasRecientes)
  const enAlerta = stats.alertas24h > 0

  return (
    <PageShell
      index="01"
      title="Tablero"
      subtitle="Vista general en tiempo real de tu red de detección"
      actions={(
        <span className={`tag ${conectado ? 'tag-moss' : 'tag-mute'}`}>
          <span className={`dot ${conectado ? 'bg-moss-400 animate-blink' : 'bg-ash-600'}`}/>
          {conectado ? 'Enlace en vivo' : 'Sin enlace'}
        </span>
      )}
    >
      {/* Módulo de estado: bento asimétrico 7/5 con hairlines internas */}
      <section className="grid grid-cols-12 border border-line mb-14 lg:mb-20 animate-rise">
        <div className={`relative col-span-12 lg:col-span-7 bg-char-850 p-7 sm:p-10 lg:p-12
                         border-b lg:border-b-0 lg:border-r border-line overflow-hidden
                         ${enAlerta ? 'border-t-2 border-t-ember-500' : ''}`}>
          {/* Lavado de calor: brasa si hay alerta, musgo si está sano */}
          <div className={`absolute inset-0 pointer-events-none
                           ${enAlerta ? 'bg-heat-wash' : 'bg-moss-wash'}`}/>
          <div className="relative">
            <p className="kicker">
              Estado del sistema
              <span className={`dot ml-3 align-middle ${enAlerta ? 'bg-ember-500 animate-blink' : 'bg-moss-400 animate-blink'}`}/>
            </p>
            <p className={`num-display uppercase mt-5 lg:mt-8 text-[clamp(2.6rem,6vw,4.5rem)]
                           ${enAlerta
                             ? 'text-fire glow-ember'
                             : 'text-moss-300 [text-shadow:0_0_28px_rgba(151,165,103,0.35)]'}`}>
              {enAlerta ? 'Alerta' : 'Nominal'}
            </p>
            <p className="font-mono text-[13px] text-ash-300 mt-5 lg:mt-8 leading-relaxed">
              <span className={enAlerta ? 'text-ember-300' : 'text-moss-300'}>
                {stats.alertas24h} alerta{stats.alertas24h === 1 ? '' : 's'}
              </span>
              {' '}en las últimas 24 h
              <span className="mx-3 text-ash-500">·</span>
              {stats.activos}/{stats.total} dispositivos reportando
            </p>
            {enAlerta && (
              <Link to="/alertas"
                className="btn-bare link-grow text-ember-400 hover:text-ember-300 inline-block mt-4">
                Revisar pendientes →
              </Link>
            )}
          </div>
        </div>
        <div className="col-span-12 lg:col-span-5 grid divide-y divide-line">
          <DataRow
            label="Temperatura media"
            value={stats.tempProm !== null ? stats.tempProm.toFixed(1) : '——'}
            unit="°C"
            color="text-ember-300"
          />
          <DataRow
            label="Humedad media"
            value={stats.humProm !== null ? stats.humProm.toFixed(0) : '——'}
            unit="%"
            color="text-flare-300"
          />
          <DataRow
            label="Dispositivos activos"
            value={`${stats.activos}`}
            unit={`/ ${stats.total}`}
            color="text-moss-300"
          />
        </div>
      </section>

      {/* Estado vacío */}
      {dispositivos.length === 0 ? (
        <EmptyState/>
      ) : (
        <div className="space-y-20 lg:space-y-28">
          {dispositivos.map((disp, i) => {
            const lectura = lecturas[disp.id]
            const tieneDatos = !!lectura
            return (
              <section key={disp.id} className="animate-fade-up">
                {/* Cabecera del dispositivo montada sobre la regla */}
                <header className="border-t border-line">
                  <div className="flex items-center justify-between gap-4 -translate-y-1/2">
                    <h2 className="bg-char-900 pr-5 flex items-baseline gap-4 min-w-0">
                      <span className="font-mono text-[11px] text-ember-400">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <span className="font-display type-expanded font-bold uppercase tracking-wide
                                       text-bone text-base sm:text-lg truncate">
                        {disp.nombre}
                      </span>
                      <span className="hidden sm:inline font-mono text-[11px] text-ash-500 truncate">
                        {disp.id}
                      </span>
                    </h2>
                    <span className={`bg-char-900 pl-5 tag ${tieneDatos ? 'tag-moss' : 'tag-mute'}`}>
                      <span className={`dot ${tieneDatos ? 'bg-moss-400 animate-blink' : 'bg-ash-600'}`}/>
                      {tieneDatos ? 'Recibiendo' : 'Sin datos'}
                    </span>
                  </div>
                </header>

                {/* Tríptico de sensores con hairlines internas */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-line border border-line mt-2 stagger">
                  <SensorCard
                    titulo="Temperatura"
                    valor={lectura?.temperatura}
                    unidad="°C"
                    color="naranja"
                  />
                  <SensorCard
                    titulo="Humedad"
                    valor={lectura?.humedad}
                    unidad="%"
                    color="azul"
                  />
                  <SensorCard
                    titulo="CO₂"
                    valor={lectura?.co2_ppm}
                    unidad="ppm"
                    color="verde"
                  />
                </div>

                <div className="mt-8">
                  <GraficoSensor dispositivoId={disp.id} />
                </div>
              </section>
            )
          })}
        </div>
      )}
    </PageShell>
  )
}

// Fila de telemetría del módulo de estado, con el valor en el color de su serie
function DataRow({ label, value, unit, color = 'text-bone' }) {
  return (
    <div className="group flex items-baseline justify-between bg-char-850 px-6 py-5 lg:px-9
                    transition-colors duration-200 hover:bg-char-800">
      <p className="kicker">{label}</p>
      <p className="flex items-baseline gap-2">
        <span className={`num-display text-2xl sm:text-3xl ${color}`}>{value}</span>
        <span className="font-mono text-[13px] text-ash-300">{unit}</span>
      </p>
    </div>
  )
}

// Estado vacío cuando no hay dispositivos registrados
function EmptyState() {
  return (
    <div className="relative border border-line p-8 sm:p-14 overflow-hidden">
      <div className="absolute inset-0 bg-heat-wash pointer-events-none"/>
      <p className="kicker relative">Red sin nodos</p>
      <h3 className="relative font-display type-expanded font-black uppercase text-bone
                     text-[clamp(1.5rem,3.4vw,2.4rem)] mt-5 max-w-lg leading-tight">
        Aún no hay dispositivos <span className="text-fire">en escucha</span>
      </h3>
      <p className="relative font-mono text-[13px] text-ash-300 mt-5 max-w-md leading-relaxed">
        Registra tu primer sensor IoT para empezar a recibir lecturas
        de temperatura, humedad y CO₂ en tiempo real.
      </p>
      <Link to="/dispositivos" className="relative btn-fire mt-9 inline-flex group">
        Agregar dispositivo
        <span className="transition-transform duration-200 ease-out-strong group-hover:translate-x-1">→</span>
      </Link>
    </div>
  )
}

// Calcula promedios y conteos para el módulo de estado
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
