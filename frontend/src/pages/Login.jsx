import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthShell from '../components/AuthShell'

// Página de inicio de sesión
export default function Login() {
  const [form, setForm]     = useState({ email: '', password: '' })
  const [error, setError]   = useState('')
  const [cargando, setCargando] = useState(false)
  const [mostrar, setMostrar] = useState(false)
  const { login }           = useAuth()
  const navigate            = useNavigate()

  // Envía credenciales y traduce errores de Firebase a texto en español
  const handleSubmit = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError('')
    try {
      await login(form.email, form.password)
      navigate('/')
    } catch (err) {
      const msg = {
        'auth/invalid-credential':    'Email o contraseña incorrectos',
        'auth/user-not-found':        'Usuario no encontrado',
        'auth/wrong-password':        'Contraseña incorrecta',
        'auth/too-many-requests':     'Demasiados intentos, intenta más tarde',
        'auth/invalid-email':         'Email inválido',
      }
      setError(msg[err.code] || 'Error al iniciar sesión')
    } finally {
      setCargando(false)
    }
  }

  return (
    <AuthShell
      title="Acceso"
      subtitle="Sistema de alerta temprana — Región del Maule"
      footer={(
        <span className="text-ash-400">
          ¿No tienes cuenta?{' '}
          <Link to="/registro"
            className="link-grow text-ember-400 hover:text-ember-300 uppercase tracking-[0.15em] ml-2">
            Crear cuenta →
          </Link>
        </span>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-7">
        <div>
          <label className="label-tech">Correo electrónico</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="input-tech"
            placeholder="correo@ejemplo.cl"
            required
            autoFocus
          />
        </div>

        <div>
          <div className="flex items-baseline justify-between mb-2">
            <label className="label-tech mb-0">Contraseña</label>
            <Link to="/recuperar"
              className="link-grow font-mono text-[11px] uppercase tracking-[0.15em]
                         text-ash-500 hover:text-ember-400 transition-colors">
              ¿Olvidaste tu clave?
            </Link>
          </div>
          <div className="relative">
            <input
              type={mostrar ? 'text' : 'password'}
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="input-tech pr-16"
              placeholder="••••••••"
              required
            />
            <button type="button" onClick={() => setMostrar(v => !v)}
              className="absolute right-4 top-1/2 -translate-y-1/2 font-mono text-[11px]
                         uppercase tracking-[0.15em] text-ash-500 hover:text-bone transition-colors">
              {mostrar ? 'Ocultar' : 'Ver'}
            </button>
          </div>
        </div>

        {error && (
          <div className="err-banner">
            <span>ERR //</span>
            <span>{error}</span>
          </div>
        )}

        <button type="submit" disabled={cargando} className="btn-fire w-full py-4">
          {cargando ? 'Verificando…' : 'Ingresar →'}
        </button>
      </form>
    </AuthShell>
  )
}
