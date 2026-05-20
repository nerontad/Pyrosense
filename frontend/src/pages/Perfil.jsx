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
    <PageShell title="Mi perfil" subtitle="Configura tus datos y notificaciones" max="max-w-3xl">
      {/* Tarjeta perfil */}
      <section className="panel overflow-hidden mb-6 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-ember-500/20 via-transparent to-red-500/10 pointer-events-none"/>
        <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-ember-500/15 blur-3xl pointer-events-none"/>
        <div className="relative p-6 sm:p-7 flex flex-col sm:flex-row items-center sm:items-end gap-5">
          <div className="relative">
            <span className="flex items-center justify-center w-20 h-20 rounded-2xl
                             bg-gradient-ember text-white font-display font-bold text-3xl
                             shadow-ember">
              {initial}
            </span>
            <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500
                             border-2 border-ink-900"/>
          </div>
          <div className="flex-1 text-center sm:text-left">
            <h2 className="font-display text-2xl font-bold text-white tracking-tight">
              {usuario?.nombre || 'Usuario'}
            </h2>
            <p className="text-zinc-400 text-sm">{usuario?.email}</p>
            <div className="flex flex-wrap gap-2 mt-3 justify-center sm:justify-start">
              <span className="chip-ok">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft"/>
                Sesión activa
              </span>
              {usuario?.telegram_chat_id
                ? <span className="chip-info">📱 Telegram conectado</span>
                : <span className="chip-mute">📱 Telegram no configurado</span>}
            </div>
          </div>
        </div>
      </section>

      {/* Telegram */}
      <Section
        icon={<IconBell/>}
        title="Notificaciones Telegram"
        desc={<>Escríbele <strong className="text-white">/start</strong> a tu bot y pega el chat_id que recibas.</>}
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <input type="text" value={telegram}
            onChange={e => setTelegram(e.target.value)}
            placeholder="Ej: 7005485756"
            className="input-base flex-1"/>
          <button onClick={guardarTelegram} disabled={cargandoTelegram}
            className="btn-ember sm:w-auto">
            {cargandoTelegram ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
        <Mensaje msg={msgTelegram}/>
      </Section>

      {/* Cambiar contraseña */}
      <Section
        icon={<IconLock/>}
        title="Cambiar contraseña"
        desc="Recomendamos una contraseña fuerte y única."
      >
        <div className="space-y-3">
          <div>
            <label className="label-base">Contraseña actual</label>
            <input type="password" value={passwords.actual}
              onChange={e => setPasswords({ ...passwords, actual: e.target.value })}
              className="input-base" placeholder="••••••••"/>
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="label-base">Nueva contraseña</label>
              <input type="password" value={passwords.nueva}
                onChange={e => setPasswords({ ...passwords, nueva: e.target.value })}
                className="input-base" placeholder="Mínimo 6 caracteres"/>
            </div>
            <div>
              <label className="label-base">Confirmar</label>
              <input type="password" value={passwords.confirmar}
                onChange={e => setPasswords({ ...passwords, confirmar: e.target.value })}
                className="input-base" placeholder="Repite la nueva contraseña"/>
            </div>
          </div>
          <Mensaje msg={msgPassword}/>
          <button onClick={guardarPassword} disabled={cargandoPassword}
            className="btn-ember w-full mt-1">
            {cargandoPassword ? 'Actualizando...' : 'Actualizar contraseña'}
          </button>
        </div>
      </Section>
    </PageShell>
  )
}

// Bloque visual para cada sección del perfil
function Section({ icon, title, desc, children }) {
  return (
    <section className="panel p-5 sm:p-6 mb-5">
      <div className="flex items-start gap-3 mb-4">
        <span className="flex items-center justify-center w-10 h-10 rounded-xl
                         bg-ember-500/10 border border-ember-500/30 text-ember-300 shrink-0">
          {icon}
        </span>
        <div>
          <h3 className="text-white font-display font-semibold tracking-tight">{title}</h3>
          {desc && <p className="text-zinc-400 text-sm mt-0.5">{desc}</p>}
        </div>
      </div>
      {children}
    </section>
  )
}

// Banner de mensaje OK / error
function Mensaje({ msg }) {
  if (!msg.texto) return null
  const ok = msg.tipo === 'ok'
  return (
    <div className={`flex items-start gap-2.5 mt-3 rounded-xl px-3.5 py-2.5 text-sm border
                     ${ok
                       ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                       : 'bg-red-500/10 border-red-500/30 text-red-300'}`}>
      <span className="text-base leading-none">{ok ? '✓' : '⚠'}</span>
      <span>{msg.texto}</span>
    </div>
  )
}

function IconBell() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
    </svg>
  )
}
function IconLock() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
      <rect x="3" y="11" width="18" height="11" rx="2"/>
      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </svg>
  )
}
