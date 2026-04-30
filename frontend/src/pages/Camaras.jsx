import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import VideoPlayer from '../components/VideoPlayer'
import api from '../services/api'

export default function Camaras() {
  const [camaras, setCamaras] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    api.get('/camaras/')
      .then(res => setCamaras(res.data))
      .finally(() => setCargando(false))
  }, [])

  const toggleStream = async (cam) => {
    if (cam.streamActivo) {
      await api.post(`/camaras/${cam.id}/stream/detener`)
    } else {
      await api.post(`/camaras/${cam.id}/stream/iniciar`)
    }
    setCamaras(prev => prev.map(c =>
      c.id === cam.id ? { ...c, streamActivo: !c.streamActivo } : c
    ))
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-white text-2xl font-bold mb-6">Cámaras</h1>

        {cargando ? (
          <p className="text-gray-400">Cargando cámaras...</p>
        ) : camaras.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-4xl mb-3">📷</div>
            <p>No hay cámaras registradas.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {camaras.map(cam => (
              <div key={cam.id} className="bg-gray-800 rounded-xl overflow-hidden">
                <VideoPlayer urlHls={`http://localhost:8888/${cam.id}/index.m3u8`} />
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold">{cam.nombre}</h3>
                      <p className="text-gray-400 text-sm truncate">{cam.url_rtsp}</p>
                    </div>
                    <button
                      onClick={() => toggleStream(cam)}
                      className={`text-sm px-4 py-2 rounded-lg font-medium transition-colors ${
                        cam.streamActivo
                          ? 'bg-red-700 hover:bg-red-600 text-white'
                          : 'bg-orange-600 hover:bg-orange-500 text-white'
                      }`}
                    >
                      {cam.streamActivo ? 'Detener' : 'Iniciar detección'}
                    </button>
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