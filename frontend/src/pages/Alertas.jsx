import Navbar from '../components/Navbar'
import AlertaBadge from '../components/AlertaBadge'
import { useEffect, useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import api from '../services/api'

export default function Alertas() {
  const [alertas, setAlertas] = useState([])
  const [cargando, setCargando] = useState(true)
  const { datos } = useWebSocket('/ws/alertas')

  useEffect(() => {
    api.get('/alertas/?limite=30')
      .then(res => setAlertas(res.data))
      .finally(() => setCargando(false))
  }, [])

  useEffect(() => {
    if (datos?.tipo === 'nueva_alerta') {
      api.get('/alertas/?limite=30').then(res => setAlertas(res.data))
    }
  }, [datos])

  const marcarRevisada = async (id) => {
    await api.patch(`/alertas/${id}/revisar`)
    setAlertas(prev => prev.map(a => a.id === id ? { ...a, revisado: true } : a))
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-white text-2xl font-bold mb-6">Alertas</h1>

        {cargando ? (
          <p className="text-gray-400">Cargando alertas...</p>
        ) : alertas.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-4xl mb-3">✅</div>
            <p>No hay alertas registradas.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alertas.map(alerta => (
              <div key={alerta.id}
                className={`bg-gray-800 rounded-xl p-4 border ${
                  alerta.revisado ? 'border-gray-700' : 'border-red-700'
                }`}
              >
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3">
                    <AlertaBadge
                      clase={alerta.tipo_id === 1 ? 'fire' : 'smoke'}
                      confianza={alerta.confianza}
                    />
                    <span className="text-gray-400 text-sm">
                      {new Date(alerta.ocurrido_en).toLocaleString('es-CL')}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {alerta.video && (
                      <a
                        href={"http://127.0.0.1:8000/videos/" + alerta.video.ruta_archivo.split(/[\\/]/).pop()}
                        target="_blank"
                        rel="noreferrer"
                        className="text-orange-400 hover:text-orange-300 text-sm"
                      >
                        Ver video
                      </a>
                    )}
                    {!alerta.revisado && (
                      <button
                        onClick={() => marcarRevisada(alerta.id)}
                        className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm px-3 py-1 rounded-lg"
                      >
                        Marcar revisada
                      </button>
                    )}
                    {alerta.revisado && (
                      <span className="text-green-500 text-sm">✓ Revisada</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}