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
      icon="🔑"
      title="Recuperar contraseña"
      subtitle="Te enviaremos un enlace para restablecerla"
      footer={(
        <Link to="/login" className="text-zinc-400 hover:text-ember-300">
          ← Volver al inicio de sesión
        </Link>
      )}
    >
      {enviado ? (
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full
                          bg-emerald-500/15 border border-emerald-500/30">
            <svg className="w-7 h-7 text-emerald-400" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <div>
            <p className="text-white font-medium">Correo enviado</p>
            <p className="text-zinc-400 text-sm mt-1">
              Revisa la bandeja de <span className="text-emerald-300">{email}</span>
            </p>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label-base">Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="input-base"
              placeholder="correo@ejemplo.cl"
              required
              autoFocus
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
                Enviando...
              </>
            ) : 'Enviar correo de recuperación'}
          </button>
        </form>
      )}
    </AuthShell>
  )
}
