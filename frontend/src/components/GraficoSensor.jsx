import { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Area, AreaChart, Legend
} from 'recharts'
import api from '../services/api'

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

  // Series disponibles en el gráfico
  const series = [
    { key: 'temperatura', label: 'Temp °C',    color: '#ff7a36' },
    { key: 'humedad',     label: 'Humedad %',  color: '#38bdf8' },
    { key: 'co2',         label: 'CO₂ ppm',    color: '#34d399' },
  ]
  const activa = series.find(s => s.key === serie)

  if (!cargando && datos.length === 0) {
    return (
      <div className="panel p-6 text-center text-zinc-500 text-sm">
        Sin lecturas históricas todavía
      </div>
    )
  }

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <div>
          <h3 className="text-white font-semibold text-sm">Historial de lecturas</h3>
          <p className="text-zinc-500 text-xs mt-0.5">Últimas 30 muestras</p>
        </div>
        <div className="flex p-1 rounded-xl bg-white/[0.03] border border-white/[0.06]">
          {series.map(s => (
            <button
              key={s.key}
              onClick={() => setSerie(s.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition
                          ${serie === s.key
                            ? 'bg-white/[0.08] text-white shadow-sm'
                            : 'text-zinc-400 hover:text-white'}`}
              style={serie === s.key ? { boxShadow: `inset 0 0 0 1px ${s.color}55` } : {}}
            >
              <span className="inline-block w-2 h-2 rounded-full mr-2" style={{ background: s.color }}/>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={datos} margin={{ top: 5, right: 8, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id={`grad-${dispositivoId}-${serie}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor={activa.color} stopOpacity={0.5}/>
              <stop offset="100%" stopColor={activa.color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false}/>
          <XAxis dataKey="hora" tick={{ fill: '#71717a', fontSize: 10 }} tickLine={false} axisLine={false}/>
          <YAxis tick={{ fill: '#71717a', fontSize: 10 }} tickLine={false} axisLine={false} width={40}/>
          <Tooltip
            contentStyle={{
              background: 'rgba(11,16,32,0.92)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '12px',
              backdropFilter: 'blur(8px)',
              fontSize: 12,
            }}
            labelStyle={{ color: '#a1a1aa' }}
            cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeDasharray: 4 }}
          />
          <Area
            type="monotone"
            dataKey={serie}
            stroke={activa.color}
            strokeWidth={2}
            fill={`url(#grad-${dispositivoId}-${serie})`}
            dot={false}
            activeDot={{ r: 4, stroke: activa.color, strokeWidth: 2, fill: '#0b1020' }}
            name={activa.label}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
