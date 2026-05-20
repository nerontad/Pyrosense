import { useEffect, useState } from 'react'
import PageShell from '../components/PageShell'
import Modal from '../components/Modal'
import api from '../services/api'

// Página para administrar dispositivos IoT y sus ubicaciones
export default function Dispositivos() {
  const [dispositivos, setDispositivos] = useState([])
  const [ubicaciones, setUbicaciones]   = useState([])
  const [cargando, setCargando]         = useState(true)
  const [tabActiva, setTabActiva]       = useState('dispositivos')

  const [modalDisp, setModalDisp]         = useState(false)
  const [formDisp, setFormDisp]           = useState({ nombre: '', ubicacion_id: '' })
  const [errorDisp, setErrorDisp]         = useState('')
  const [guardandoDisp, setGuardandoDisp] = useState(false)

  const [modalUbi, setModalUbi]           = useState(false)
  const [formUbi, setFormUbi]             = useState({ nombre: '', descripcion: '' })
  const [errorUbi, setErrorUbi]           = useState('')
  const [guardandoUbi, setGuardandoUbi]   = useState(false)

  useEffect(() => { cargarDatos() }, [])

  // Carga dispositivos y ubicaciones en paralelo
  const cargarDatos = async () => {
    setCargando(true)
    try {
      const [resDisp, resUbi] = await Promise.all([
        api.get('/dispositivos/'),
        api.get('/ubicaciones/')
      ])
      setDispositivos(resDisp.data)
      setUbicaciones(resUbi.data)
    } catch {} finally { setCargando(false) }
  }

  // ── Dispositivos ──
  const abrirModalDisp = () => {
    setFormDisp({ nombre: '', ubicacion_id: ubicaciones[0]?.id || '' })
    setErrorDisp('')
    setModalDisp(true)
  }

  // Crea un nuevo dispositivo IoT
  const guardarDispositivo = async () => {
    if (!formDisp.nombre || !formDisp.ubicacion_id) {
      setErrorDisp('Todos los campos son obligatorios'); return
    }
    setGuardandoDisp(true); setErrorDisp('')
    try {
      await api.post('/dispositivos/', {
        nombre: formDisp.nombre,
        ubicacion_id: formDisp.ubicacion_id,
        tipo_id: 1
      })
      await cargarDatos()
      setModalDisp(false)
      setFormDisp({ nombre: '', ubicacion_id: '' })
    } catch (err) {
      setErrorDisp(err.response?.data?.detail || 'Error al guardar')
    } finally { setGuardandoDisp(false) }
  }

  // Activa o desactiva un dispositivo
  const toggleDisp = async (disp) => {
    await api.patch(`/dispositivos/${disp.id}`, { activo: !disp.activo })
    setDispositivos(prev => prev.map(d => d.id === disp.id ? { ...d, activo: !d.activo } : d))
  }

  // Elimina un dispositivo tras confirmación
  const eliminarDisp = async (id) => {
    if (!confirm('¿Eliminar este dispositivo?')) return
    try {
      await api.delete(`/dispositivos/${id}`)
      setDispositivos(prev => prev.filter(d => d.id !== id))
    } catch { alert('Error al eliminar el dispositivo') }
  }

  // ── Ubicaciones ──
  const abrirModalUbi = () => {
    setFormUbi({ nombre: '', descripcion: '' })
    setErrorUbi('')
    setModalUbi(true)
  }

  // Crea una nueva ubicación
  const guardarUbicacion = async () => {
    if (!formUbi.nombre) { setErrorUbi('El nombre es obligatorio'); return }
    setGuardandoUbi(true); setErrorUbi('')
    try {
      await api.post('/ubicaciones/', formUbi)
      await cargarDatos()
      setModalUbi(false)
      setFormUbi({ nombre: '', descripcion: '' })
    } catch (err) {
      setErrorUbi(err.response?.data?.detail || 'Error al guardar')
    } finally { setGuardandoUbi(false) }
  }

  // Elimina una ubicación (falla si está en uso)
  const eliminarUbi = async (id) => {
    if (!confirm('¿Eliminar esta ubicación?')) return
    try {
      await api.delete(`/ubicaciones/${id}`)
      setUbicaciones(prev => prev.filter(u => u.id !== id))
    } catch { alert('No se puede eliminar una ubicación en uso') }
  }

  return (
    <PageShell
      title="Dispositivos IoT"
      subtitle="Gestiona sensores y ubicaciones de tu red"
      max="max-w-5xl"
      actions={(
        tabActiva === 'dispositivos'
          ? <button onClick={abrirModalDisp} className="btn-ember">+ Agregar dispositivo</button>
          : <button onClick={abrirModalUbi}  className="btn-ember">+ Agregar ubicación</button>
      )}
    >
      {/* Tabs */}
      <div className="flex p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] mb-6 w-fit">
        <TabBtn active={tabActiva === 'dispositivos'} onClick={() => setTabActiva('dispositivos')}>
          📡 Dispositivos
          <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded-md bg-white/[0.06]">
            {dispositivos.length}
          </span>
        </TabBtn>
        <TabBtn active={tabActiva === 'ubicaciones'} onClick={() => setTabActiva('ubicaciones')}>
          📍 Ubicaciones
          <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded-md bg-white/[0.06]">
            {ubicaciones.length}
          </span>
        </TabBtn>
      </div>

      {cargando ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1,2,3].map(i => (
            <div key={i} className="panel p-5 h-44 animate-shimmer shimmer-bg"/>
          ))}
        </div>
      ) : tabActiva === 'dispositivos' ? (
        dispositivos.length === 0 ? (
          <Empty title="Sin dispositivos registrados" desc="Agrega tu primer sensor IoT"
                 icon="📡" cta="+ Agregar primer dispositivo" onClick={abrirModalDisp}/>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {dispositivos.map(disp => {
              const ubi = ubicaciones.find(u => u.id === disp.ubicacion_id)
              return (
                <article key={disp.id}
                  className="panel panel-hover p-5 relative overflow-hidden animate-fade-in-up">
                  <div className={`absolute -top-12 -right-12 w-32 h-32 rounded-full blur-2xl
                                   ${disp.activo
                                     ? 'bg-gradient-to-br from-emerald-500/20 to-transparent'
                                     : 'bg-gradient-to-br from-zinc-500/10 to-transparent'}`}/>
                  <div className="relative">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-11 h-11 rounded-xl
                                         bg-gradient-to-br from-ember-500/20 to-red-500/10
                                         border border-ember-500/30 text-xl">
                          📡
                        </span>
                        <div>
                          <h3 className="text-white font-display font-semibold tracking-tight">
                            {disp.nombre}
                          </h3>
                          <p className="text-xs text-zinc-500">📍 {ubi?.nombre || 'Sin ubicación'}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className={disp.activo ? 'chip-ok' : 'chip-mute'}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            disp.activo ? 'bg-emerald-400 animate-pulse-soft' : 'bg-zinc-500'
                          }`}/>
                          {disp.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mt-3">
                      <span className="chip-ember">🌡️ Temp.</span>
                      <span className="chip-info">💧 Humedad</span>
                      <span className="chip-ok">💨 CO₂</span>
                    </div>

                    <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
                      <p className="text-[10px] text-zinc-600 font-mono truncate max-w-[60%]">
                        {disp.id}
                      </p>
                      <div className="flex gap-2">
                        <button onClick={() => toggleDisp(disp)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition
                                      ${disp.activo
                                        ? 'bg-white/[0.04] text-zinc-300 hover:bg-white/[0.08]'
                                        : 'bg-gradient-ember text-white hover:brightness-110'}`}>
                          {disp.activo ? 'Desactivar' : 'Activar'}
                        </button>
                        <button onClick={() => eliminarDisp(disp.id)}
                          className="p-1.5 rounded-lg text-zinc-400 hover:text-red-300 hover:bg-red-500/10 transition"
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
        )
      ) : (
        ubicaciones.length === 0 ? (
          <Empty title="Sin ubicaciones registradas" desc="Crea ubicaciones para asignar dispositivos"
                 icon="📍" cta="+ Agregar primera ubicación" onClick={abrirModalUbi}/>
        ) : (
          <div className="space-y-3">
            {ubicaciones.map(ubi => (
              <article key={ubi.id}
                className="panel panel-hover p-4 flex items-center justify-between gap-4
                           animate-fade-in-up">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="flex items-center justify-center w-10 h-10 rounded-xl
                                   bg-sky-500/10 border border-sky-500/30 text-lg">
                    📍
                  </span>
                  <div className="min-w-0">
                    <h3 className="text-white font-display font-semibold tracking-tight truncate">
                      {ubi.nombre}
                    </h3>
                    {ubi.descripcion && (
                      <p className="text-zinc-400 text-sm mt-0.5 truncate">{ubi.descripcion}</p>
                    )}
                    <p className="text-zinc-600 text-[10px] font-mono mt-1">{ubi.id}</p>
                  </div>
                </div>
                <button onClick={() => eliminarUbi(ubi.id)}
                  className="p-2 rounded-lg text-zinc-400 hover:text-red-300 hover:bg-red-500/10 transition shrink-0"
                  title="Eliminar">
                  <IconTrash/>
                </button>
              </article>
            ))}
          </div>
        )
      )}

      {/* Modal dispositivo */}
      <Modal
        open={modalDisp}
        onClose={() => setModalDisp(false)}
        title="Agregar dispositivo IoT"
        subtitle="Incluye sensores de temperatura, humedad y CO₂/gas"
        footer={(
          <>
            <button onClick={() => setModalDisp(false)} className="btn-ghost flex-1">Cancelar</button>
            <button onClick={guardarDispositivo} disabled={guardandoDisp || ubicaciones.length === 0}
              className="btn-ember flex-1">
              {guardandoDisp ? 'Guardando...' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-4">
          <div>
            <label className="label-base">Nombre del dispositivo</label>
            <input type="text" value={formDisp.nombre}
              onChange={e => setFormDisp({ ...formDisp, nombre: e.target.value })}
              className="input-base" placeholder="Ej: Sensor bodega norte"/>
          </div>
          <div>
            <label className="label-base">Ubicación</label>
            {ubicaciones.length === 0 ? (
              <div className="bg-amber-500/10 border border-amber-500/30 text-amber-300
                              rounded-xl px-3.5 py-3 text-sm">
                ⚠ Crea primero una ubicación en la pestaña <strong>Ubicaciones</strong>.
              </div>
            ) : (
              <select value={formDisp.ubicacion_id}
                onChange={e => setFormDisp({ ...formDisp, ubicacion_id: e.target.value })}
                className="input-base">
                <option value="">Selecciona una ubicación</option>
                {ubicaciones.map(u => <option key={u.id} value={u.id}>{u.nombre}</option>)}
              </select>
            )}
          </div>
          <div className="rounded-xl bg-white/[0.02] border border-white/[0.06] p-3.5">
            <p className="text-[10px] uppercase tracking-wider text-zinc-500 mb-2">
              Sensores incluidos
            </p>
            <div className="flex flex-wrap gap-1.5">
              <span className="chip-ember">🌡️ Temperatura</span>
              <span className="chip-info">💧 Humedad</span>
              <span className="chip-ok">💨 CO₂ / Gas</span>
            </div>
          </div>
          {errorDisp && <p className="text-red-400 text-sm">{errorDisp}</p>}
        </div>
      </Modal>

      {/* Modal ubicación */}
      <Modal
        open={modalUbi}
        onClose={() => setModalUbi(false)}
        title="Agregar ubicación"
        subtitle="Espacio físico donde instalarás dispositivos"
        footer={(
          <>
            <button onClick={() => setModalUbi(false)} className="btn-ghost flex-1">Cancelar</button>
            <button onClick={guardarUbicacion} disabled={guardandoUbi} className="btn-ember flex-1">
              {guardandoUbi ? 'Guardando...' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-4">
          <div>
            <label className="label-base">Nombre</label>
            <input type="text" value={formUbi.nombre}
              onChange={e => setFormUbi({ ...formUbi, nombre: e.target.value })}
              className="input-base" placeholder="Ej: Bodega principal"/>
          </div>
          <div>
            <label className="label-base">Descripción (opcional)</label>
            <input type="text" value={formUbi.descripcion}
              onChange={e => setFormUbi({ ...formUbi, descripcion: e.target.value })}
              className="input-base" placeholder="Ej: Zona norte del edificio"/>
          </div>
          {errorUbi && <p className="text-red-400 text-sm">{errorUbi}</p>}
        </div>
      </Modal>
    </PageShell>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button onClick={onClick}
      className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition flex items-center
                  ${active
                    ? 'bg-white/[0.08] text-white shadow-inner'
                    : 'text-zinc-400 hover:text-white'}`}>
      {children}
    </button>
  )
}

function Empty({ title, desc, icon, cta, onClick }) {
  return (
    <div className="panel py-16 text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl
                      bg-gradient-to-br from-ember-500/20 to-red-500/10
                      border border-ember-500/30 mb-4">
        <span className="text-3xl">{icon}</span>
      </div>
      <h3 className="text-white font-display text-lg font-semibold">{title}</h3>
      <p className="text-zinc-400 text-sm mt-1.5">{desc}</p>
      <button onClick={onClick} className="btn-ember mt-5">{cta}</button>
    </div>
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
