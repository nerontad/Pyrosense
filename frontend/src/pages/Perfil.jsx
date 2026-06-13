import { useState } from 'react'
import PageShell from '../components/PageShell'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

// Página de cuenta del usuario: Telegram y contraseña
export default function Perfil() {
  const { usuario, cambiarPassword } = useAuth()

  const [telegram, setTelegram]         = useState(usuario?.telegram_chat_id || '')
  const [msgTelegram, setMsgTelegram]   = useState({ tipo: '', texto: '' })

  const [passwords, setPasswords]       = useState({ actual: '', nueva: '', confirmar: '' })
  const [msgPassword, setMsgPassword]   = useState({ tipo: '', texto: '' })

  const [cargandoTelegram, setCargandoTelegram]   = useState(false)
  const [cargandoPassword, setCargandoPassword]   = useState(false)

  const initial = (usuario?.nombre || usuario?.email || '?')[0].toUpperCase()

  // Guarda el chat_id de Telegram en el perfil del usuario
  const guardarTelegram = async () => {
    setCargandoTelegram(true)
    setMsgTelegram({ tipo: '', texto: '' })
    try {
      await api.patch(`/usuarios/me/telegram?chat_id=${telegram}`)
      setMsgTelegram({ tipo: 'ok', texto: 'Telegram configurado correctamente' })
    } catch {
      setMsgTelegram({ tipo: 'err', texto: 'Error al guardar' })
    } finally {
      setCargandoTelegram(false)
    }
  }

  // Cambia la contraseña en Firebase tras validar
  const guardarPassword = async () => {
    setMsgPassword({ tipo: '', texto: '' })
    if (passwords.nueva !== passwords.confirmar) {
      setMsgPassword({ tipo: 'err', texto: 'Las contraseñas nuevas no coinciden' }); return
    }
    if (passwords.nueva.length < 6) {
      setMsgPassword({ tipo: 'err', texto: 'La contraseña debe tener al menos 6 caracteres' }); return
    }
    setCargandoPassword(true)
    try {
      await cambiarPassword(passwords.actual, passwords.nueva)
      setMsgPassword({ tipo: 'ok', texto: 'Contraseña actualizada correctamente' })
      setPasswords({ actual: '', nueva: '', confirmar: '' })
    } catch (err) {
      const msg = {
        'auth/wrong-password':           'Contraseña actual incorrecta',
        'auth/too-many-requests':        'Demasiados intentos, intenta más tarde',
        'auth/requires-recent-login':    'Sesión expirada, vuelve a iniciar sesión',
      }
      setMsgPassword({ tipo: 'err', texto: msg[err.code] || 'Error al cambiar contraseña' })
    } finally {
      setCargandoPassword(false)
    }
  }

  return (
    <PageShell
      index="05"
      title="Operador"
      subtitle="Configura tus datos y canales de notificación"
    >
      {/* Split asimétrico: identidad 4 / ajustes 8.
          En móvil el bloque de identidad se vuelve horizontal para no ocupar toda la pantalla. */}
      <div className="grid grid-cols-12 gap-x-10 gap-y-12">
        {/* Bloque de identidad */}
        <aside className="col-span-12 lg:col-span-4">
          <div className="border border-line animate-rise flex flex-row lg:flex-col">
            <div className="relative w-28 sm:w-36 lg:w-full aspect-square shrink-0
                            flex items-center justify-center
                            border-r lg:border-r-0 lg:border-b border-line
                            bg-char-850 overflow-hidden">
              <div className="absolute inset-0 bg-heat-wash pointer-events-none"/>
              <span className="relative num-display text-5xl sm:text-6xl lg:text-7xl
                               text-fire glow-ember select-none">{initial}</span>
            </div>
            <div className="p-5 sm:p-6 lg:p-8 min-w-0 flex-1">
              <h2 className="font-display type-expanded font-bold uppercase tracking-wide
                             text-bone text-lg lg:text-xl leading-tight break-words">
                {usuario?.nombre || 'Usuario'}
              </h2>
              <p className="font-mono text-[13px] text-ash-300 mt-2 lg:mt-3 break-all">
                {usuario?.email}
              </p>
              <div className="flex flex-row flex-wrap lg:flex-col items-start gap-2 mt-4 lg:mt-7">
                <span className="tag tag-moss">
                  <span className="dot bg-moss-400 animate-blink"/>
                  Sesión activa
                </span>
                {usuario?.telegram_chat_id
                  ? <span className="tag tag-mute">Telegram enlazado</span>
                  : <span className="tag tag-flare">Telegram sin configurar</span>}
              </div>
            </div>
          </div>
        </aside>

        {/* Ajustes */}
        <div className="col-span-12 lg:col-span-8 space-y-16">
          <Section
            num="A"
            title="Notificaciones Telegram"
            desc={<>Escríbele <span className="text-bone">/start</span> a tu bot y pega el chat_id que recibas.</>}
          >
            <div className="flex flex-col sm:flex-row gap-3">
              <input type="text" value={telegram}
                onChange={e => setTelegram(e.target.value)}
                placeholder="Ej: 7005485756"
                className="input-tech font-mono flex-1"/>
              <button onClick={guardarTelegram} disabled={cargandoTelegram}
                className="btn-fire sm:w-auto">
                {cargandoTelegram ? 'Guardando…' : 'Guardar'}
              </button>
            </div>
            <Mensaje msg={msgTelegram}/>
          </Section>

          <Section
            num="B"
            title="Cambiar contraseña"
            desc="Recomendamos una contraseña fuerte y única."
          >
            <div className="space-y-5">
              <div>
                <label className="label-tech">Contraseña actual</label>
                <input type="password" value={passwords.actual}
                  onChange={e => setPasswords({ ...passwords, actual: e.target.value })}
                  className="input-tech" placeholder="••••••••"/>
              </div>
              <div className="grid sm:grid-cols-2 gap-5">
                <div>
                  <label className="label-tech">Nueva contraseña</label>
                  <input type="password" value={passwords.nueva}
                    onChange={e => setPasswords({ ...passwords, nueva: e.target.value })}
                    className="input-tech" placeholder="Mínimo 6 caracteres"/>
                </div>
                <div>
                  <label className="label-tech">Confirmar</label>
                  <input type="password" value={passwords.confirmar}
                    onChange={e => setPasswords({ ...passwords, confirmar: e.target.value })}
                    className="input-tech" placeholder="Repite la nueva contraseña"/>
                </div>
              </div>
              <Mensaje msg={msgPassword}/>
              <button onClick={guardarPassword} disabled={cargandoPassword}
                className="btn-fire w-full">
                {cargandoPassword ? 'Actualizando…' : 'Actualizar contraseña'}
              </button>
            </div>
          </Section>
        </div>
      </div>
    </PageShell>
  )
}

// Sección de ajustes con etiqueta montada sobre la regla
function Section({ num, title, desc, children }) {
  return (
    <section>
      <header className="border-t border-line">
        <div className="-translate-y-1/2">
          <h3 className="inline-flex items-baseline gap-4 bg-char-900 pr-5">
            <span className="font-mono text-[11px] text-ember-500">{num}</span>
            <span className="font-display type-expanded font-bold uppercase tracking-wide
                             text-bone text-base">
              {title}
            </span>
          </h3>
        </div>
      </header>
      {desc && (
        <p className="font-mono text-[13px] text-ash-300 mb-6 tracking-wide leading-relaxed">
          {desc}
        </p>
      )}
      {children}
    </section>
  )
}

// Banner de mensaje OK / error
function Mensaje({ msg }) {
  if (!msg.texto) return null
  const ok = msg.tipo === 'ok'
  return (
    <div className={`flex items-start gap-3 mt-4 px-4 py-3 border font-mono text-[13px] animate-fade-up
                     ${ok
                       ? 'border-moss-500/60 text-moss-300'
                       : 'border-ember-500/50 text-ember-300'}`}>
      <span>{ok ? 'OK //' : 'ERR //'}</span>
      <span>{msg.texto}</span>
    </div>
  )
}
