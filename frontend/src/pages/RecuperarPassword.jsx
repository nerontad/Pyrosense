import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthShell from '../components/AuthShell'

// Página para enviar un correo de recuperación de contraseña
export default function RecuperarPassword() {
  const [email, setEmail]       = useState('')
  const [enviado, setEnviado]   = useState(false)
  const [error, setError]       = useState('')
  const [cargando, setCargando] = useState(false)
  const { recuperarPassword }   = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError('')
    try {
      await recuperarPassword(email)
      setEnviado(true)
    } catch (err) {
      const msg = {
        'auth/user-not-found': 'No existe una cuenta con ese email',
        'auth/invalid-email':  'Email inválido',
      }
      setError(msg[err.code] || 'Error al enviar el correo')
    } finally {
      setCargando(false)
    }
  }

  return (
    <AuthShell
      title="Recuperar clave"
      subtitle="Te enviaremos un enlace para restablecerla"
      footer={(
        <Link to="/login"
          className="link-grow text-ash-400 hover:text-bone uppercase tracking-[0.15em]">
          ← Volver al inicio de sesión
        </Link>
      )}
    >
      {enviado ? (
        <div className="animate-fade-up">
          <p className="num-display uppercase text-4xl text-moss-300">Enviado →</p>
          <p className="font-mono text-[15px] text-ash-300 mt-6 leading-relaxed">
            Revisa la bandeja de <span className="text-bone">{email}</span>.
            <br/>El enlace de restablecimiento expira pronto.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-7">
          <div>
            <label className="label-tech">Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="input-tech"
              placeholder="correo@ejemplo.cl"
              required
              autoFocus
            />
          </div>

          {error && (
            <div className="err-banner">
              <span>ERR //</span>
              <span>{error}</span>
            </div>
          )}

          <button type="submit" disabled={cargando} className="btn-fire w-full py-4">
            {cargando ? 'Enviando…' : 'Enviar correo de recuperación →'}
          </button>
        </form>
      )}
    </AuthShell>
  )
}
