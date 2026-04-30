import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import api from '../services/api'

export default function Dispositivos() {
  const [dispositivos, setDispositivos] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    api.get('/dispositivos/')
      .then(res => setDispositivos(res.data))
      .finally(() => setCargando(false))
  }, [])

  const toggleActivo = async (disp) => {
    await api.patch(`/dispositivos/${disp.id}`, { activo: !disp.activo })
    setDispositivos(prev => prev.map(d =>
      d.id === disp.id ? { ...d, activo: !d.activo } : d
    ))
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-white text-2xl font-bold mb-6">Dispositivos IoT</h1>

        {cargando ? (
          <p className="text-gray-400">Cargando dispositivos...</p>
        ) : dispositivos.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-4xl mb-3">📡</div>
            <p>No hay dispositivos registrados.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {dispositivos.map(disp => (
              <div key={disp.id} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">📡</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    disp.activo
                      ? 'bg-green-900/50 text-green-400 border border-green-700'
                      : 'bg-gray-700 text-gray-400'
                  }`}>
                    {disp.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
                <h3 className="text-white font-semibold mb-1">{disp.nombre}</h3>
                <p className="text-gray-400 text-xs mb-4">
                  {new Date(disp.creado_en).toLocaleDateString('es-CL')}
                </p>
                <button
                  onClick={() => toggleActivo(disp)}
                  className={`w-full text-sm py-2 rounded-lg transition-colors ${
                    disp.activo
                      ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                      : 'bg-orange-600 hover:bg-orange-500 text-white'
                  }`}
                >
                  {disp.activo ? 'Desactivar' : 'Activar'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}