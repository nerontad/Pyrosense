import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import api from '../services/api'

export default function GraficoSensor({ dispositivoId }) {
  const [datos, setDatos] = useState([])

  useEffect(() => {
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
  }, [dispositivoId])

  if (datos.length === 0) return null

  return (
    <div className="bg-gray-800 rounded-xl p-4">
      <h3 className="text-gray-400 text-sm mb-3">Historial de lecturas</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={datos}>
          <XAxis dataKey="hora" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
            labelStyle={{ color: '#f9fafb' }}
          />
          <Legend />
          <Line type="monotone" dataKey="temperatura" stroke="#f97316" dot={false} name="Temp °C" />
          <Line type="monotone" dataKey="humedad"     stroke="#3b82f6" dot={false} name="Humedad %" />
          <Line type="monotone" dataKey="co2"         stroke="#22c55e" dot={false} name="CO₂ ppm" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}