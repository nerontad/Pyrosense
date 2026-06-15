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
      title="Registro"
      subtitle="Comienza a vigilar tu infraestructura en minutos"
      footer={(
        <span className="text-ash-400">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login"
            className="link-grow text-ember-400 hover:text-ember-300 uppercase tracking-[0.15em] ml-2">
            Inicia sesión →
          </Link>
        </span>
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-7">
        <div>
          <label className="label-tech">Nombre</label>
          <input
            type="text"
            value={form.nombre}
            onChange={e => setForm({ ...form, nombre: e.target.value })}
            className="input-tech"
            placeholder="Tu nombre"
            required
            autoFocus
          />
        </div>

        <div>
          <label className="label-tech">Correo electrónico</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="input-tech"
            placeholder="correo@ejemplo.cl"
            required
          />
        </div>

        <div>
          <label className="label-tech">Contraseña</label>
          <input
            type="password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            className="input-tech"
            placeholder="Mínimo 6 caracteres"
            required
          />
          {form.password && (
            <div className="mt-3">
              {/* Medidor de fuerza: 4 segmentos lineales */}
              <div className="flex gap-1">
                {[1, 2, 3, 4].map(i => (
                  <span key={i} className="flex-1 h-[3px] transition-colors duration-300"
                    style={{ background: i <= fuerza.nivel ? fuerza.color : 'rgba(237,230,218,0.13)' }}/>
                ))}
              </div>
              <p className="font-mono text-[13px] uppercase tracking-[0.2em] mt-2"
                 style={{ color: fuerza.color }}>
                {fuerza.label}
              </p>
            </div>
          )}
        </div>

        <div>
          <label className="label-tech">Confirmar contraseña</label>
          <input
            type="password"
            value={form.confirmar}
            onChange={e => setForm({ ...form, confirmar: e.target.value })}
            className={`input-tech ${form.confirmar && form.password !== form.confirmar
              ? 'border-ember-500/70 focus:border-ember-500' : ''}`}
            placeholder="Repite la contraseña"
            required
          />
        </div>

        {error && (
          <div className="err-banner">
            <span>ERR //</span>
            <span>{error}</span>
          </div>
        )}

        <button type="submit" disabled={cargando} className="btn-fire w-full py-4">
          {cargando ? 'Creando cuenta…' : 'Crear cuenta →'}
        </button>
      </form>
    </AuthShell>
  )
}

// Calcula la fortaleza de la contraseña (0 a 4) con colores del sistema
function calcularFuerza(p) {
  if (!p) return { nivel: 0, label: '', color: '' }
  let n = 0
  if (p.length >= 6)                 n++
  if (p.length >= 10)                n++
  if (/[A-Z]/.test(p) && /\d/.test(p)) n++
  if (/[^A-Za-z0-9]/.test(p))        n++
  const map = [
    { label: 'Muy débil', color: '#D63E00' },
    { label: 'Débil',     color: '#FF4D00' },
    { label: 'Aceptable', color: '#E0A458' },
    { label: 'Buena',     color: '#97A567' },
    { label: 'Excelente', color: '#BAC49A' },
  ]
  return { nivel: n, ...map[n] }
}
