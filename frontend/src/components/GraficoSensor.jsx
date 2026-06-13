import { useEffect, useState } from 'react'
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Area, AreaChart
} from 'recharts'
import api from '../services/api'

// Series disponibles en el gráfico (paleta cálida del sistema)
const SERIES = [
  { key: 'temperatura', label: 'Temp °C',   color: '#FF6A26' },
  { key: 'humedad',     label: 'Humedad %', color: '#E0A458' },
  { key: 'co2',         label: 'CO₂ ppm',   color: '#97A567' },
]

// Gráfico de área con histórico de lecturas (temp / humedad / CO₂)
export default function GraficoSensor({ dispositivoId }) {
  const [datos, setDatos] = useState([])
  const [serie, setSerie] = useState('temperatura')
  const [cargando, setCargando] = useState(true)

  // Carga las últimas 30 lecturas del dispositivo
  useEffect(() => {
    setCargando(true)
    api.get(`/lecturas/${dispositivoId}?limite=30`)
      .then(res => {
        const formateados = res.data.reverse().map(l => ({
          hora: new Date(l.registrado_en).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }),
          temperatura: l.temperatura,
          humedad: l.humedad,
          co2: l.co2_ppm
        }))
        setDatos(formateados)
      })
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [dispositivoId])

  const activa = SERIES.find(s => s.key === serie)

  if (!cargando && datos.length === 0) {
    return (
      <div className="border border-line px-6 py-10 font-mono text-[13px] text-ash-400">
        // Sin lecturas históricas todavía
      </div>
    )
  }

  return (
    <div className="mod">
      <div className="flex items-center justify-between flex-wrap gap-x-6 gap-y-3
                      px-6 sm:px-8 pt-5 border-b border-line">
        <p className="kicker pb-4">
          Historial — últimas 30 muestras
        </p>
        {/* Selector de serie: tabs con subrayado en el color de la serie */}
        <div className="flex gap-1">
          {SERIES.map(s => (
            <button
              key={s.key}
              onClick={() => setSerie(s.key)}
              className={`px-3 pb-4 font-mono text-[11px] uppercase tracking-[0.18em]
                          border-b-2 transition-colors duration-200
                          ${serie === s.key
                            ? ''
                            : 'text-ash-500 border-transparent hover:text-bone'}`}
              style={serie === s.key ? { borderColor: s.color, color: s.color } : {}}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-3 sm:px-5 py-6">
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={datos} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
            <defs>
              <linearGradient id={`grad-${dispositivoId}-${serie}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor={activa.color} stopOpacity={0.32}/>
                <stop offset="100%" stopColor={activa.color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(244,237,223,0.07)" vertical={false}/>
            <XAxis dataKey="hora" tick={{ fill: '#ADA193', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              tickLine={false} axisLine={{ stroke: 'rgba(244,237,223,0.16)' }}/>
            <YAxis tick={{ fill: '#ADA193', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              tickLine={false} axisLine={false} width={44}/>
            <Tooltip
              contentStyle={{
                background: '#16100A',
                border: '1px solid rgba(244,237,223,0.3)',
                borderRadius: 0,
                fontSize: 12,
                fontFamily: 'JetBrains Mono',
              }}
              labelStyle={{ color: '#CCC1B2' }}
              cursor={{ stroke: 'rgba(237,230,218,0.2)', strokeDasharray: 3 }}
            />
            <Area
              type="monotone"
              dataKey={serie}
              stroke={activa.color}
              strokeWidth={2}
              fill={`url(#grad-${dispositivoId}-${serie})`}
              dot={false}
              activeDot={{ r: 3, stroke: activa.color, strokeWidth: 1.5, fill: '#0E0C0A' }}
              name={activa.label}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
