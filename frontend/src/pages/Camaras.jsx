import { useEffect, useState } from 'react'
import PageShell from '../components/PageShell'
import VideoPlayer from '../components/VideoPlayer'
import Modal from '../components/Modal'
import api from '../services/api'

// URL base del servidor de streams HLS
const VPS_URL = 'https://detector-incendios.duckdns.org'

// Página de gestión de cámaras con visualización en vivo
export default function Camaras() {
  const [camaras, setCamaras]           = useState([])
  const [ubicaciones, setUbicaciones]   = useState([])
  const [cargando, setCargando]         = useState(true)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [editando, setEditando]         = useState(null)
  const [form, setForm]                 = useState({ nombre: '', url_rtsp: '', ubicacion_id: '' })
  const [error, setError]               = useState('')
  const [guardando, setGuardando]       = useState(false)

  useEffect(() => { cargarDatos() }, [])

  // Carga cámaras y ubicaciones en paralelo
  const cargarDatos = async () => {
    setCargando(true)
    try {
      const [resCam, resUbi] = await Promise.all([
        api.get('/camaras/'),
        api.get('/ubicaciones/')
      ])
      setCamaras(resCam.data)
      setUbicaciones(resUbi.data)
    } catch {
      setError('Error al cargar datos')
    } finally {
      setCargando(false)
    }
  }

  // Abre el modal en modo crear o editar
  const abrirModal = (camara = null) => {
    setEditando(camara)
    setForm(camara
      ? { nombre: camara.nombre, url_rtsp: camara.url_rtsp, ubicacion_id: camara.ubicacion_id }
      : { nombre: '', url_rtsp: '', ubicacion_id: ubicaciones[0]?.id || '' }
    )
    setError('')
    setModalAbierto(true)
  }

  const cerrarModal = () => {
    setModalAbierto(false)
    setEditando(null)
    setForm({ nombre: '', url_rtsp: '', ubicacion_id: '' })
    setError('')
  }

  // Crea o actualiza la cámara en el backend
  const guardar = async () => {
    if (!form.nombre || !form.url_rtsp || !form.ubicacion_id) {
      setError('Todos los campos son obligatorios')
      return
    }
    setGuardando(true)
    setError('')
    try {
      if (editando) {
        await api.patch(`/camaras/${editando.id}`, form)
      } else {
        await api.post('/camaras/', form)
      }
      await cargarDatos()
      cerrarModal()
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar')
    } finally {
      setGuardando(false)
    }
  }

  // Elimina la cámara tras confirmación
  const eliminar = async (id) => {
    if (!confirm('¿Eliminar esta cámara?')) return
    try {
      await api.delete(`/camaras/${id}`)
      setCamaras(prev => prev.filter(c => c.id !== id))
    } catch {
      alert('Error al eliminar')
    }
  }

  return (
    <PageShell
      title="Cámaras"
      subtitle="Vigilancia visual en vivo con detección automática de fuego"
      actions={(
        <button onClick={() => abrirModal()} className="btn-ember">
          <span className="text-base leading-none">+</span> Agregar cámara
        </button>
      )}
    >
      {cargando ? (
        <SkeletonGrid/>
      ) : camaras.length === 0 ? (
        <div className="panel py-16 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl
                          bg-gradient-to-br from-ember-500/20 to-red-500/10
                          border border-ember-500/30 mb-4">
            <span className="text-3xl">📷</span>
          </div>
          <h3 className="text-white font-display text-lg font-semibold">
            Sin cámaras registradas
          </h3>
          <p className="text-zinc-400 text-sm mt-1.5">
            Agrega tu primera cámara RTSP para empezar la vigilancia.
          </p>
          <button onClick={() => abrirModal()} className="btn-ember mt-5">
            + Agregar primera cámara
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {camaras.map(cam => {
            const ubi = ubicaciones.find(u => u.id === cam.ubicacion_id)
            return (
              <article key={cam.id} className="panel panel-hover overflow-hidden animate-fade-in-up">
                <VideoPlayer urlHls={`${VPS_URL}/${cam.id}/index.m3u8`} />
                <div className="p-4 sm:p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <h3 className="text-white font-display font-semibold text-base tracking-tight">
                        {cam.nombre}
                      </h3>
                      <div className="flex items-center gap-2 mt-1.5 text-xs text-zinc-500">
                        <span className="inline-flex items-center gap-1">
                          📍 {ubi?.nombre || 'Sin ubicación'}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-600 font-mono mt-2 truncate">
                        {cam.url_rtsp}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        <span className="chip-ok">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft"/>
                          Detección activa
                        </span>
                        <span className="chip-ember">YOLO · Fuego/Humo</span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <button onClick={() => abrirModal(cam)}
                        className="p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition"
                        title="Editar">
                        <IconPencil/>
                      </button>
                      <button onClick={() => eliminar(cam.id)}
                        className="p-2 rounded-lg text-zinc-400 hover:text-red-300 hover:bg-red-500/10 transition"
                        title="Eliminar">
                        <IconTrash/>
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      )}

      <Modal
        open={modalAbierto}
        onClose={cerrarModal}
        title={editando ? 'Editar cámara' : 'Agregar cámara'}
        subtitle="Define el flujo RTSP y dónde está instalada"
        footer={(
          <>
            <button onClick={cerrarModal} className="btn-ghost flex-1">Cancelar</button>
            <button onClick={guardar} disabled={guardando} className="btn-ember flex-1">
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-4">
          <div>
            <label className="label-base">Nombre</label>
            <input type="text" value={form.nombre}
              onChange={e => setForm({ ...form, nombre: e.target.value })}
              className="input-base" placeholder="Ej: Cámara bodega norte"/>
          </div>
          <div>
            <label className="label-base">URL RTSP</label>
            <input type="text" value={form.url_rtsp}
              onChange={e => setForm({ ...form, url_rtsp: e.target.value })}
              className="input-base font-mono text-sm"
              placeholder="rtsp://usuario:contraseña@ip/stream"/>
          </div>
          <div>
            <label className="label-base">Ubicación</label>
            <select value={form.ubicacion_id}
              onChange={e => setForm({ ...form, ubicacion_id: e.target.value })}
              className="input-base">
              <option value="">Selecciona una ubicación</option>
              {ubicaciones.map(u => (
                <option key={u.id} value={u.id}>{u.nombre}</option>
              ))}
            </select>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>
      </Modal>
    </PageShell>
  )
}

// Placeholder mientras cargan las cámaras
function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {[1,2].map(i => (
        <div key={i} className="panel overflow-hidden">
          <div className="aspect-video bg-white/[0.03] shimmer-bg animate-shimmer"/>
          <div className="p-5 space-y-2">
            <div className="h-4 w-1/3 bg-white/[0.06] rounded animate-shimmer shimmer-bg"/>
            <div className="h-3 w-2/3 bg-white/[0.04] rounded animate-shimmer shimmer-bg"/>
          </div>
        </div>
      ))}
    </div>
  )
}

function IconPencil() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  )
}
function IconTrash() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
      <polyline points="3 6 5 6 21 6"/>
      <path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    </svg>
  )
}
