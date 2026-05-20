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
      title="Bienvenido de vuelta"
      subtitle="Sistema de alerta temprana — Región del Maule"
      footer={(
        <span className="text-zinc-400">
          ¿No tienes cuenta?{' '}
          <Link to="/registro" className="text-ember-400 hover:text-ember-300 font-medium">
            Crear cuenta
          </Link>
        </span>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label-base">Correo electrónico</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="input-base"
            placeholder="correo@ejemplo.cl"
            required
            autoFocus
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="label-base mb-0">Contraseña</label>
            <Link to="/recuperar" className="text-xs text-zinc-400 hover:text-ember-300">
              ¿Olvidaste tu clave?
            </Link>
          </div>
          <div className="relative">
            <input
              type={mostrar ? 'text' : 'password'}
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="input-base pr-12"
              placeholder="••••••••"
              required
            />
            <button type="button" onClick={() => setMostrar(v => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500
                         hover:text-zinc-300 text-xs font-semibold uppercase tracking-wider">
              {mostrar ? 'Ocultar' : 'Ver'}
            </button>
          </div>
        </div>

        {error && (
          <div className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/30
                          text-red-300 rounded-xl px-3.5 py-3 text-sm animate-fade-in-up">
            <span className="text-base leading-none">⚠</span>
            <span>{error}</span>
          </div>
        )}

        <button type="submit" disabled={cargando} className="btn-ember w-full py-3 text-base">
          {cargando ? (
            <>
              <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"/>
              Iniciando sesión...
            </>
          ) : 'Ingresar'}
        </button>
      </form>
    </AuthShell>
  )
}
