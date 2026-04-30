import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const linkClass = (path) =>
    `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      location.pathname === path
        ? 'bg-orange-600 text-white'
        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔥</span>
            <span className="text-white font-bold text-lg hidden sm:block">
              Detector Incendios
            </span>
          </div>

          {/* Links */}
          <div className="flex items-center gap-1">
            <Link to="/" className={linkClass('/')}>Dashboard</Link>
            <Link to="/camaras" className={linkClass('/camaras')}>Cámaras</Link>
            <Link to="/alertas" className={linkClass('/alertas')}>Alertas</Link>
            <Link to="/dispositivos" className={linkClass('/dispositivos')}>IoT</Link>
          </div>

          {/* Usuario */}
          <div className="flex items-center gap-3">
            <span className="text-gray-400 text-sm hidden sm:block">
              {usuario?.nombre}
            </span>
            <button
              onClick={handleLogout}
              className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm px-3 py-2 rounded-lg transition-colors"
            >
              Salir
            </button>
          </div>

        </div>
      </div>
    </nav>
  )
}