import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthShell from '../components/AuthShell'

// Página de registro de nuevo usuario
export default function Registro() {
  const [form, setForm] = useState({ nombre: '', email: '', password: '', confirmar: '' })
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const { registro } = useAuth()
  const navigate = useNavigate()

  // Nivel de seguridad de la contraseña ingresada
  const fuerza = calcularFuerza(form.password)

  // Valida y crea la cuenta en Firebase
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (form.password !== form.confirmar) {
      setError('Las contraseñas no coinciden')
      return
    }
    if (form.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres')
      return
    }

    setCargando(true)
    try {
      await registro(form.email, form.password, form.nombre)
      navigate('/')
    } catch (err) {
      const msg = {
        'auth/email-already-in-use': 'Este email ya está registrado',
        'auth/invalid-email':        'Email inválido',
        'auth/weak-password':        'Contraseña muy débil',
      }
      setError(msg[err.code] || 'Error al crear la cuenta')
    } finally {
      setCargando(false)
    }
  }

  return (
    <AuthShell
      title="Crear cuenta"
      subtitle="Comienza a vigilar tu infraestructura en minutos"
      footer={(
        <span className="text-zinc-400">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-ember-400 hover:text-ember-300 font-medium">
            Inicia sesión
          </Link>
        </span>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label-base">Nombre</label>
          <input
            type="text"
            value={form.nombre}
            onChange={e => setForm({ ...form, nombre: e.target.value })}
            className="input-base"
            placeholder="Tu nombre"
            required
            autoFocus
          />
        </div>

        <div>
          <label className="label-base">Correo electrónico</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="input-base"
            placeholder="correo@ejemplo.cl"
            required
          />
        </div>

        <div>
          <label className="label-base">Contraseña</label>
          <input
            type="password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            className="input-base"
            placeholder="Mínimo 6 caracteres"
            required
          />
          {form.password && (
            <div className="mt-2 space-y-1">
              <div className="h-1.5 rounded-full bg-white/[0.05] overflow-hidden flex gap-0.5">
                {[1,2,3,4].map(i => (
                  <span key={i} className={`flex-1 transition-all ${
                    i <= fuerza.nivel ? fuerza.color : 'bg-transparent'
                  }`}/>
                ))}
              </div>
              <p className={`text-[11px] ${fuerza.text}`}>{fuerza.label}</p>
            </div>
          )}
        </div>

        <div>
          <label className="label-base">Confirmar contraseña</label>
          <input
            type="password"
            value={form.confirmar}
            onChange={e => setForm({ ...form, confirmar: e.target.value })}
            className={`input-base ${form.confirmar && form.password !== form.confirmar ? 'border-red-500/50 focus:border-red-500' : ''}`}
            placeholder="Repite la contraseña"
            required
          />
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
              Creando cuenta...
            </>
          ) : 'Crear cuenta'}
        </button>
      </form>
    </AuthShell>
  )
}

// Calcula la fortaleza de la contraseña (0 a 4)
function calcularFuerza(p) {
  if (!p) return { nivel: 0, label: '', color: '', text: '' }
  let n = 0
  if (p.length >= 6)                 n++
  if (p.length >= 10)                n++
  if (/[A-Z]/.test(p) && /\d/.test(p)) n++
  if (/[^A-Za-z0-9]/.test(p))        n++
  const map = [
    { label: 'Muy débil',  color: 'bg-red-500',     text: 'text-red-400' },
    { label: 'Débil',      color: 'bg-orange-500',  text: 'text-orange-300' },
    { label: 'Aceptable',  color: 'bg-amber-500',   text: 'text-amber-300' },
    { label: 'Buena',      color: 'bg-lime-500',    text: 'text-lime-300' },
    { label: 'Excelente',  color: 'bg-emerald-500', text: 'text-emerald-300' },
  ]
  return { nivel: n, ...map[n] }
}
