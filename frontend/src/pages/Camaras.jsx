import { useEffect, useState } from 'react'
import PageShell from '../components/PageShell'
import VideoPlayer from '../components/VideoPlayer'
import DetectorLocal from '../components/DetectorLocal'
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
  const [demoAbierto, setDemoAbierto]   = useState(false)

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
      index="02"
      title="Cámaras"
      subtitle="Vigilancia visual en vivo con detección automática de fuego"
      actions={(
        <>
          <button onClick={() => setDemoAbierto(v => !v)} className="btn-line">
            {demoAbierto ? 'Ocultar demo' : 'Demo con mi cámara'}
          </button>
          <button onClick={() => abrirModal()} className="btn-fire">
            + Agregar cámara
          </button>
        </>
      )}
    >
      {demoAbierto && (
        <section className="mb-16 animate-fade-up">
          <header className="border-t border-line mb-2">
            <div className="-translate-y-1/2">
              <h2 className="inline-block bg-char-900 pr-5 font-display type-expanded font-bold
                             uppercase tracking-wide text-bone text-base sm:text-lg">
                Demo en vivo
              </h2>
            </div>
          </header>
          <p className="font-mono text-[13px] text-ash-300 mb-6 tracking-wide">
            Usa la cámara de tu notebook o celular para probar la detección de fuego/humo en tiempo real.
          </p>
          <DetectorLocal />
        </section>
      )}

      {cargando ? (
        <SkeletonGrid/>
      ) : camaras.length === 0 ? (
        <div className="relative border border-line p-8 sm:p-14 overflow-hidden">
          <div className="absolute inset-0 bg-heat-wash pointer-events-none"/>
          <p className="kicker relative">Sin señal de video</p>
          <h3 className="relative font-display type-expanded font-black uppercase text-bone
                         text-[clamp(1.5rem,3.4vw,2.4rem)] mt-5 max-w-lg leading-tight">
            Ningún punto de <span className="text-fire">vigilancia</span> activo
          </h3>
          <p className="relative font-mono text-[13px] text-ash-300 mt-5 max-w-md leading-relaxed">
            Agrega tu primera cámara RTSP para que el modelo de visión
            empiece a vigilar el perímetro.
          </p>
          <button onClick={() => abrirModal()} className="relative btn-fire mt-9">
            + Agregar primera cámara
          </button>
        </div>
      ) : (
        // Grilla de vigilancia: 3 cámaras por fila en pantallas grandes
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-px bg-line border border-line stagger">
          {camaras.map((cam, i) => {
            const ubi = ubicaciones.find(u => u.id === cam.ubicacion_id)
            return (
              <article key={cam.id} className="group bg-char-850 flex flex-col">
                {/* Cabecera compacta del módulo de cámara */}
                <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-line
                                transition-colors duration-200 group-hover:border-b-line-ember">
                  <div className="flex items-baseline gap-3 min-w-0">
                    <span className="font-mono text-[11px] text-ember-400 shrink-0">
                      C{String(i + 1).padStart(2, '0')}
                    </span>
                    <h3 className="font-display type-expanded font-bold uppercase tracking-wide
                                   text-bone text-[13px] truncate">
                      {cam.nombre}
                    </h3>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <button onClick={() => abrirModal(cam)} className="btn-bare link-grow">
                      Editar
                    </button>
                    <button onClick={() => eliminar(cam.id)}
                      className="btn-bare link-grow text-ash-500 hover:text-ember-400">
                      Eliminar
                    </button>
                  </div>
                </div>

                <VideoPlayer urlHls={`${VPS_URL}/${cam.id}/index.m3u8`} />

                {/* Pie con ubicación y motor de detección */}
                <div className="flex items-center justify-between gap-3 px-4 py-2.5 border-t border-line mt-auto">
                  <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-ash-400 truncate"
                     title={cam.url_rtsp}>
                    ↳ {ubi?.nombre || 'Sin ubicación'}
                  </p>
                  <span className="tag tag-ember shrink-0">YOLO</span>
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
            <button onClick={cerrarModal} className="btn-line flex-1">Cancelar</button>
            <button onClick={guardar} disabled={guardando} className="btn-fire flex-1">
              {guardando ? 'Guardando…' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-5">
          <div>
            <label className="label-tech">Nombre</label>
            <input type="text" value={form.nombre}
              onChange={e => setForm({ ...form, nombre: e.target.value })}
              className="input-tech" placeholder="Ej: Cámara bodega norte"/>
          </div>
          <div>
            <label className="label-tech">URL RTSP</label>
            <input type="text" value={form.url_rtsp}
              onChange={e => setForm({ ...form, url_rtsp: e.target.value })}
              className="input-tech font-mono text-xs"
              placeholder="rtsp://usuario:contraseña@ip/stream"/>
          </div>
          <div>
            <label className="label-tech">Ubicación</label>
            <select value={form.ubicacion_id}
              onChange={e => setForm({ ...form, ubicacion_id: e.target.value })}
              className="input-tech">
              <option value="">Selecciona una ubicación</option>
              {ubicaciones.map(u => (
                <option key={u.id} value={u.id}>{u.nombre}</option>
              ))}
            </select>
          </div>
          {error && (
            <p className="err-banner">
              <span>ERR //</span>
              <span>{error}</span>
            </p>
          )}
        </div>
      </Modal>
    </PageShell>
  )
}

// Placeholder mientras cargan las cámaras
function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-px bg-line border border-line">
      {[1, 2, 3].map(i => (
        <div key={i} className="bg-char-850">
          <div className="h-11 border-b border-line shimmer-bg animate-shimmer"/>
          <div className="aspect-video shimmer-bg animate-shimmer"/>
        </div>
      ))}
    </div>
  )
}
