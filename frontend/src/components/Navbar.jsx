import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useEffect, useState } from 'react'

// Items del menú principal
const NAV_ITEMS = [
  { to: '/',             label: 'Tablero',  icon: IconDashboard },
  { to: '/camaras',      label: 'Cámaras',  icon: IconCamera },
  { to: '/alertas',      label: 'Alertas',  icon: IconAlert },
  { to: '/dispositivos', label: 'IoT',      icon: IconChip },
]

// Navegación principal: spine vertical ultrafina en desktop, topbar + drawer en móvil
export default function Navbar() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [movilAbierto, setMovilAbierto] = useState(false)

  // Cierra el drawer móvil al cambiar de ruta
  useEffect(() => {
    setMovilAbierto(false)
  }, [location.pathname])

  // Cierra sesión y redirige al login
  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const initial = (usuario?.nombre || usuario?.email || '?')[0].toUpperCase()

  return (
    <>
      {/* Spine desktop */}
      <aside className="hidden lg:flex fixed left-0 top-0 h-full w-[76px] z-30 flex-col
                        bg-char-900 border-r border-line">
        {/* Marca */}
        <Link to="/" aria-label="Pyrosense"
          className="group relative flex items-center justify-center h-[76px] border-b border-line
                     text-ember-500 transition-colors duration-200 hover:text-ember-300">
          <span className="absolute inset-0 bg-heat-wash opacity-60 pointer-events-none"/>
          <span className="relative animate-flicker"><IconFlame/></span>
        </Link>

        {/* Navegación */}
        <nav className="flex flex-col">
          {NAV_ITEMS.map(item => (
            <SpineLink key={item.to} item={item} active={location.pathname === item.to}/>
          ))}
        </nav>

        {/* Wordmark vertical: solo la marca para que SIEMPRE calce en el alto de la spine.
            La etiqueta completa ("Vigilancia de incendios") vive en el topbar móvil y el póster de acceso. */}
        <div className="flex-1 flex items-center justify-center min-h-0 overflow-hidden py-6">
          <span
            className="font-mono text-[15px] font-medium uppercase tracking-[0.32em] text-ash-400 select-none whitespace-nowrap
                       [@media(max-height:700px)]:hidden"
            style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}
          >
            Pyrosense
          </span>
        </div>

        {/* Perfil + salida */}
        <div className="border-t border-line">
          <Link to="/perfil" title={usuario?.email || 'Mi perfil'}
            className={`flex items-center justify-center h-16 border-b border-line
                        font-display font-bold text-sm transition-colors
                        ${location.pathname === '/perfil'
                          ? 'text-ember-400'
                          : 'text-ash-400 hover:text-bone'}`}>
            <span className="flex items-center justify-center w-8 h-8 border border-line">
              {initial}
            </span>
          </Link>
          <button onClick={handleLogout} title="Cerrar sesión" aria-label="Cerrar sesión"
            className="flex items-center justify-center w-full h-14
                       text-ash-500 transition-colors hover:text-ember-400">
            <IconLogout/>
          </button>
        </div>
      </aside>

      {/* Topbar móvil */}
      <header className="lg:hidden sticky top-0 z-40 bg-char-900 border-b border-line">
        <div className="flex items-center justify-between h-14 pl-4 pr-2">
          <Link to="/" className="flex items-center gap-3 text-ember-500">
            <IconFlame small/>
            <span className="font-mono text-[13px] uppercase tracking-mega text-bone">
              Pyrosense
            </span>
          </Link>
          <button
            onClick={() => setMovilAbierto(v => !v)}
            className="p-3 text-ash-300 hover:text-bone transition-colors"
            aria-label="Menú"
          >
            {movilAbierto ? <IconX/> : <IconMenu/>}
          </button>
        </div>

        {/* Drawer móvil: navegación tipo registro */}
        {movilAbierto && (
          <nav className="border-t border-line stagger">
            {NAV_ITEMS.map((item, i) => {
              const active = location.pathname === item.to
              return (
                <Link key={item.to} to={item.to}
                  className={`flex items-baseline justify-between px-5 py-4 border-b border-line
                              transition-colors
                              ${active ? 'text-ember-400' : 'text-ash-300 hover:text-bone'}`}>
                  <span className="flex items-baseline gap-4">
                    <span className="font-mono text-[13px] text-ash-500">0{i + 1}</span>
                    <span className="font-display type-expanded font-bold uppercase tracking-wide text-sm">
                      {item.label}
                    </span>
                  </span>
                  {active && <span className="dot bg-ember-500"/>}
                </Link>
              )
            })}
            <Link to="/perfil"
              className="flex items-center justify-between px-5 py-4 border-b border-line
                         text-ash-300 hover:text-bone transition-colors">
              <span className="font-mono text-[14px] uppercase tracking-[0.2em]">
                {usuario?.nombre || 'Mi perfil'}
              </span>
              <span className="font-mono text-[13px] text-ash-500 truncate max-w-[50%]">
                {usuario?.email}
              </span>
            </Link>
            <button onClick={handleLogout}
              className="w-full text-left px-5 py-4 font-mono text-[14px] uppercase
                         tracking-[0.2em] text-ember-400 hover:bg-char-850 transition-colors">
              Cerrar sesión →
            </button>
          </nav>
        )}
      </header>
    </>
  )
}

// Enlace de la spine: icono + microetiqueta, barra brasa cuando está activo
function SpineLink({ item, active }) {
  const Icon = item.icon
  return (
    <Link
      to={item.to}
      className={`group relative flex flex-col items-center gap-1.5 py-5 border-b border-line
                  transition-colors duration-200
                  ${active
                    ? 'text-ember-400 bg-gradient-to-r from-ember-500/15 to-transparent'
                    : 'text-ash-500 hover:text-bone'}`}
    >
      {active && (
        <span className="absolute left-0 top-0 bottom-0 w-[3px] bg-ember-500
                         shadow-[2px_0_12px_rgba(255,77,0,0.5)]"/>
      )}
      <span className="transition-transform duration-200 ease-out-strong group-hover:-translate-y-0.5">
        <Icon/>
      </span>
      <span className="font-mono text-[12px] uppercase tracking-[0.18em]">
        {item.label}
      </span>
    </Link>
  )
}

/* ─── Iconos inline ─── */
function IconFlame({ small }) {
  const s = small ? 18 : 22
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2c1 3 4 5 4 9a4 4 0 1 1-8 0c0-2 1-3 1-5-2 1-4 4-4 7a7 7 0 1 0 14 0c0-5-4-7-7-11Z"/>
    </svg>
  )
}
function IconDashboard() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="7" height="9"/>
      <rect x="14" y="3" width="7" height="5"/>
      <rect x="14" y="12" width="7" height="9"/>
      <rect x="3" y="16" width="7" height="5"/>
    </svg>
  )
}
function IconCamera() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M3 8h3l2-3h8l2 3h3v11H3z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  )
}
function IconAlert() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
      <path d="M12 3 1.8 21h20.4L12 3z"/>
      <line x1="12" y1="10" x2="12" y2="15"/>
      <circle cx="12" cy="17.5" r="0.5" fill="currentColor"/>
    </svg>
  )
}
function IconChip() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="6" y="6" width="12" height="12"/>
      <path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>
    </svg>
  )
}
function IconLogout() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="square">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  )
}
function IconMenu() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="3" y1="7" x2="21" y2="7"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
      <line x1="3" y1="17" x2="21" y2="17"/>
    </svg>
  )
}
function IconX() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  )
}
