import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import SensorCard from '../components/SensorCard'
import GraficoSensor from '../components/GraficoSensor'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

export default function Dashboard() {
  const [dispositivos, setDispositivos] = useState([])
  const [lecturas, setLecturas] = useState({})
  const { datos, conectado } = useWebSocket('/ws/sensores')

  useEffect(() => {
    api.get('/dispositivos/').then(res => setDispositivos(res.data))
  }, [])

  useEffect(() => {
    if (!datos) return
    if (datos.tipo === 'lecturas_iniciales') {
      setLecturas(datos.datos)
    } else if (datos.dispositivo_id) {
      setLecturas(prev => ({
        ...prev,
        [datos.dispositivo_id]: datos
      }))
    }
  }, [datos])

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-6">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-white text-2xl font-bold">Dashboard</h1>
          <span className={`flex items-center gap-2 text-sm px-3 py-1 rounded-full ${
            conectado
              ? 'bg-green-900/50 text-green-400 border border-green-700'
              : 'bg-gray-700 text-gray-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${conectado ? 'bg-green-400' : 'bg-gray-500'}`}/>
            {conectado ? 'En vivo' : 'Desconectado'}
          </span>
        </div>

        {/* Dispositivos */}
        {dispositivos.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-4xl mb-3">📡</div>
            <p>No hay dispositivos IoT registrados.</p>
            <p className="text-sm mt-1">Ve a la sección IoT para agregar uno.</p>
          </div>
        ) : (
          dispositivos.map(disp => {
            const lectura = lecturas[disp.id]
            return (
              <div key={disp.id} className="mb-8">
                <h2 className="text-gray-300 font-semibold mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-500"/>
                  {disp.nombre}
                </h2>
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
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}