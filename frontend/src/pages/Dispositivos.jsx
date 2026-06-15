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
      index="04"
      title="Red IoT"
      subtitle="Gestiona sensores y ubicaciones de tu red"
      actions={(
        tabActiva === 'dispositivos'
          ? <button onClick={abrirModalDisp} className="btn-fire">+ Agregar dispositivo</button>
          : <button onClick={abrirModalUbi}  className="btn-fire">+ Agregar ubicación</button>
      )}
    >
      {/* Tabs con subrayado */}
      <div className="flex gap-1 border-b border-line mb-10 overflow-x-auto [&::-webkit-scrollbar]:hidden">
        <TabBtn active={tabActiva === 'dispositivos'} onClick={() => setTabActiva('dispositivos')}>
          Dispositivos
          <span className="ml-3 text-ash-500 tabular-nums">{dispositivos.length}</span>
        </TabBtn>
        <TabBtn active={tabActiva === 'ubicaciones'} onClick={() => setTabActiva('ubicaciones')}>
          Ubicaciones
          <span className="ml-3 text-ash-500 tabular-nums">{ubicaciones.length}</span>
        </TabBtn>
      </div>

      {cargando ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-line border border-line">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-char-850 h-44 shimmer-bg animate-shimmer"/>
          ))}
        </div>
      ) : tabActiva === 'dispositivos' ? (
        dispositivos.length === 0 ? (
          <Empty title="Ningún nodo en la red"
                 desc="Registra tu primer sensor IoT para empezar a recibir telemetría."
                 kicker="Red sin nodos"
                 cta="+ Agregar primer dispositivo" onClick={abrirModalDisp}/>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-px bg-line border border-line stagger">
            {dispositivos.map((disp, i) => {
              const ubi = ubicaciones.find(u => u.id === disp.ubicacion_id)
              return (
                <article key={disp.id}
                  className="group bg-char-850 p-6 sm:p-7 transition-colors duration-200
                             hover:bg-char-800">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="font-mono text-[13px] text-ember-400">
                        N{String(i + 1).padStart(2, '0')}
                      </p>
                      <h3 className="font-display type-expanded font-bold uppercase tracking-wide
                                     text-bone text-base mt-2 truncate">
                        {disp.nombre}
                      </h3>
                      <p className="font-mono text-[13px] uppercase tracking-[0.15em] text-ash-500 mt-1.5 truncate">
                        ↳ {ubi?.nombre || 'Sin ubicación'}
                      </p>
                    </div>
                    <span className={`tag shrink-0 ${disp.activo ? 'tag-moss' : 'tag-mute'}`}>
                      <span className={`dot ${disp.activo ? 'bg-moss-400 animate-blink' : 'bg-ash-600'}`}/>
                      {disp.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2 mt-6">
                    <span className="tag tag-ember">Temp</span>
                    <span className="tag tag-flare">Humedad</span>
                    <span className="tag tag-moss">CO₂ / Gas</span>
                  </div>

                  <div className="mt-7 pt-4 border-t border-line flex items-center justify-between gap-4">
                    <p className="font-mono text-[13px] text-ash-500 truncate">
                      {disp.id}
                    </p>
                    <div className="flex items-center gap-5 shrink-0">
                      <button onClick={() => toggleDisp(disp)}
                        className={`btn-bare link-grow ${disp.activo ? '' : 'text-moss-300 hover:text-moss-300'}`}>
                        {disp.activo ? 'Desactivar' : 'Activar'}
                      </button>
                      <button onClick={() => eliminarDisp(disp.id)}
                        className="btn-bare link-grow text-ash-500 hover:text-ember-400">
                        Eliminar
                      </button>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )
      ) : (
        ubicaciones.length === 0 ? (
          <Empty title="Sin ubicaciones definidas"
                 desc="Crea ubicaciones físicas para asignar tus dispositivos."
                 kicker="Mapa vacío"
                 cta="+ Agregar primera ubicación" onClick={abrirModalUbi}/>
        ) : (
          <div className="border border-line divide-y divide-line stagger">
            {ubicaciones.map((ubi, i) => (
              <article key={ubi.id}
                className="grid grid-cols-12 items-center gap-4 px-5 sm:px-6 py-5
                           bg-char-850 hover:bg-char-800 transition-colors duration-200">
                <span className="col-span-1 font-mono text-[13px] text-ember-400">
                  U{String(i + 1).padStart(2, '0')}
                </span>
                <div className="col-span-9 sm:col-span-5 min-w-0">
                  <h3 className="font-display type-expanded font-bold uppercase tracking-wide
                                 text-bone text-sm truncate">
                    {ubi.nombre}
                  </h3>
                  <p className="font-mono text-[13px] text-ash-500 mt-1 truncate">{ubi.id}</p>
                </div>
                <p className="hidden sm:block sm:col-span-4 font-mono text-[14px] text-ash-400 truncate">
                  {ubi.descripcion || '—'}
                </p>
                <div className="col-span-2 flex justify-end">
                  <button onClick={() => eliminarUbi(ubi.id)}
                    className="btn-bare link-grow text-ash-500 hover:text-ember-400">
                    Eliminar
                  </button>
                </div>
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
            <button onClick={() => setModalDisp(false)} className="btn-line flex-1">Cancelar</button>
            <button onClick={guardarDispositivo} disabled={guardandoDisp || ubicaciones.length === 0}
              className="btn-fire flex-1">
              {guardandoDisp ? 'Guardando…' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-5">
          <div>
            <label className="label-tech">Nombre del dispositivo</label>
            <input type="text" value={formDisp.nombre}
              onChange={e => setFormDisp({ ...formDisp, nombre: e.target.value })}
              className="input-tech" placeholder="Ej: Sensor bodega norte"/>
          </div>
          <div>
            <label className="label-tech">Ubicación</label>
            {ubicaciones.length === 0 ? (
              <div className="border border-flare-500/60 text-flare-300 px-4 py-3 font-mono text-xs">
                Crea primero una ubicación en la pestaña Ubicaciones.
              </div>
            ) : (
              <select value={formDisp.ubicacion_id}
                onChange={e => setFormDisp({ ...formDisp, ubicacion_id: e.target.value })}
                className="input-tech">
                <option value="">Selecciona una ubicación</option>
                {ubicaciones.map(u => <option key={u.id} value={u.id}>{u.nombre}</option>)}
              </select>
            )}
          </div>
          <div className="border border-line p-4">
            <p className="kicker mb-3">Sensores incluidos</p>
            <div className="flex flex-wrap gap-2">
              <span className="tag tag-ember">Temperatura</span>
              <span className="tag tag-mute">Humedad</span>
              <span className="tag tag-moss">CO₂ / Gas</span>
            </div>
          </div>
          {errorDisp && (
            <p className="err-banner">
              <span>ERR //</span>
              <span>{errorDisp}</span>
            </p>
          )}
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
            <button onClick={() => setModalUbi(false)} className="btn-line flex-1">Cancelar</button>
            <button onClick={guardarUbicacion} disabled={guardandoUbi} className="btn-fire flex-1">
              {guardandoUbi ? 'Guardando…' : 'Guardar'}
            </button>
          </>
        )}
      >
        <div className="space-y-5">
          <div>
            <label className="label-tech">Nombre</label>
            <input type="text" value={formUbi.nombre}
              onChange={e => setFormUbi({ ...formUbi, nombre: e.target.value })}
              className="input-tech" placeholder="Ej: Bodega principal"/>
          </div>
          <div>
            <label className="label-tech">Descripción (opcional)</label>
            <input type="text" value={formUbi.descripcion}
              onChange={e => setFormUbi({ ...formUbi, descripcion: e.target.value })}
              className="input-tech" placeholder="Ej: Zona norte del edificio"/>
          </div>
          {errorUbi && (
            <p className="err-banner">
              <span>ERR //</span>
              <span>{errorUbi}</span>
            </p>
          )}
        </div>
      </Modal>
    </PageShell>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button onClick={onClick}
      className={`shrink-0 whitespace-nowrap px-4 pb-3 -mb-px font-mono text-[13px] uppercase tracking-[0.18em]
                  border-b-2 transition-colors duration-200
                  ${active
                    ? 'text-bone border-ember-500'
                    : 'text-ash-500 border-transparent hover:text-bone'}`}>
      {children}
    </button>
  )
}

function Empty({ kicker, title, desc, cta, onClick }) {
  return (
    <div className="relative border border-line p-8 sm:p-14 overflow-hidden">
      <div className="absolute inset-0 bg-heat-wash pointer-events-none"/>
      <p className="kicker relative">{kicker}</p>
      <h3 className="relative font-display type-expanded font-black uppercase text-bone
                     text-[clamp(1.5rem,3.4vw,2.4rem)] mt-5 max-w-lg leading-tight">
        {title}
      </h3>
      <p className="relative font-mono text-[15px] text-ash-300 mt-5 max-w-md leading-relaxed">{desc}</p>
      <button onClick={onClick} className="relative btn-fire mt-9">{cta}</button>
    </div>
  )
}
