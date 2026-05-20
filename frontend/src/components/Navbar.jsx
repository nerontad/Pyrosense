import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useEffect, useRef, useState } from 'react'

// Items del menú lateral
const NAV_ITEMS = [
  { to: '/',             label: 'Dashboard',  icon: IconDashboard },
  { to: '/camaras',      label: 'Cámaras',    icon: IconCamera },
  { to: '/alertas',      label: 'Alertas',    icon: IconAlert },
  { to: '/dispositivos', label: 'IoT',        icon: IconChip },
]

// Barra de navegación principal (sidebar en desktop, drawer en móvil)
export default function Navbar() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuAbierto, setMenuAbierto] = useState(false)
  const [movilAbierto, setMovilAbierto] = useState(false)
  const dropdownRef = useRef(null)

  // Cierra el menú de usuario al hacer clic fuera
  useEffect(() => {
    const onClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setMenuAbierto(false)
      }
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

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
      {/* Sidebar desktop — más compacto */}
      <aside className="hidden lg:flex fixed left-0 top-0 h-full w-56 z-30 flex-col
                        bg-ink-900/70 backdrop-blur-2xl border-r border-white/[0.06]">
        <Brand />
        <nav className="flex-1 px-2.5 py-2 space-y-0.5">
          {NAV_ITEMS.map(item => (
            <NavLink key={item.to} item={item} active={location.pathname === item.to} />
          ))}
        </nav>
        <SidebarFooter usuario={usuario} onLogout={handleLogout} />
      </aside>

      {/* Topbar móvil */}
      <header className="lg:hidden sticky top-0 z-40 bg-ink-900/85 backdrop-blur-xl
                         border-b border-white/[0.06]">
        <div className="flex items-center justify-between px-4 h-14">
          <Brand compact />
          <button
            onClick={() => setMovilAbierto(v => !v)}
            className="p-2 rounded-lg text-zinc-300 hover:bg-white/5 transition"
            aria-label="Menú"
          >
            {movilAbierto ? <IconX/> : <IconMenu/>}
          </button>
        </div>
        {movilAbierto && (
          <div className="border-t border-white/[0.06] px-3 py-3 space-y-0.5 animate-fade-in-up">
            {NAV_ITEMS.map(item => (
              <NavLink key={item.to} item={item} active={location.pathname === item.to} />
            ))}
            <div className="pt-2 mt-2 border-t border-white/[0.06]">
              <Link to="/perfil" className="flex items-center gap-3 px-3 py-2 rounded-lg
                                            text-zinc-300 hover:bg-white/5">
                <span className="w-7 h-7 rounded-full bg-gradient-ember flex items-center
                                 justify-center text-white text-xs font-bold">{initial}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{usuario?.nombre || 'Mi perfil'}</p>
                  <p className="text-[11px] text-zinc-500 truncate">{usuario?.email}</p>
                </div>
              </Link>
              <button onClick={handleLogout}
                className="w-full text-left px-3 py-2 rounded-lg text-sm text-red-300
                           hover:bg-red-500/10 transition">
                Cerrar sesión
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Topbar desktop (acciones) */}
      <header className="hidden lg:flex sticky top-0 z-20 ml-56 h-14
                         bg-ink-900/40 backdrop-blur-xl border-b border-white/[0.06]
                         items-center justify-end px-6 gap-3">
        <span className="hidden xl:flex chip chip-mute">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft"/>
          Sistema en línea
        </span>
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setMenuAbierto(v => !v)}
            className="flex items-center gap-2 pl-1 pr-2.5 py-1 rounded-full
                       bg-white/[0.04] border border-white/[0.08]
                       hover:bg-white/[0.08] hover:border-white/20 transition"
          >
            <span className="w-7 h-7 rounded-full bg-gradient-ember flex items-center
                             justify-center text-white text-xs font-bold shadow-ember-soft">
              {initial}
            </span>
            <span className="text-sm text-zinc-200 max-w-[140px] truncate">
              {usuario?.nombre || usuario?.email}
            </span>
            <IconChevron/>
          </button>
          {menuAbierto && (
            <div className="absolute right-0 mt-2 w-56 rounded-2xl panel shadow-glass-lg
                            overflow-hidden animate-fade-in-up">
              <div className="px-4 py-3 border-b border-white/[0.06]">
                <p className="text-sm text-white truncate font-medium">{usuario?.nombre}</p>
                <p className="text-xs text-zinc-500 truncate">{usuario?.email}</p>
              </div>
              <Link to="/perfil" onClick={() => setMenuAbierto(false)}
                className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-zinc-300
                           hover:bg-white/[0.04] hover:text-white transition">
                <IconUser/> Mi perfil
              </Link>
              <button onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-300
                           hover:bg-red-500/10 transition">
                <IconLogout/> Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </header>
    </>
  )
}

// Logo de la marca
function Brand({ compact = false }) {
  return (
    <Link to="/" className={`flex items-center gap-2.5 ${compact ? '' : 'px-4 py-4'}`}>
      <span className="relative flex items-center justify-center w-9 h-9 rounded-lg
                       bg-gradient-ember shadow-ember-soft shrink-0">
        <IconFlame/>
        <span className="absolute inset-0 rounded-lg ring-2 ring-ember-500/40
                         opacity-0 animate-glow-pulse"/>
      </span>
      <div className="leading-tight">
        <p className="text-white font-display font-bold text-[15px] tracking-tight">Pyrosense</p>
        <p className="text-[9px] text-zinc-400 uppercase tracking-[0.22em]">Fire Watch</p>
      </div>
    </Link>
  )
}

// Enlace del menú (resalta el activo)
function NavLink({ item, active }) {
  const Icon = item.icon
  return (
    <Link
      to={item.to}
      className={`group relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm
                  font-medium transition
                  ${active
                    ? 'text-white bg-gradient-to-r from-ember-500/15 to-transparent'
                    : 'text-zinc-400 hover:text-white hover:bg-white/[0.04]'}`}
    >
      {active && (
        <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-r-full
                         bg-gradient-to-b from-ember-400 to-red-500"/>
      )}
      <Icon className={active ? 'text-ember-400' : 'text-zinc-500 group-hover:text-zinc-300'}/>
      <span className="flex-1">{item.label}</span>
      {active && <span className="w-1.5 h-1.5 rounded-full bg-ember-400 animate-pulse-soft"/>}
    </Link>
  )
}

// Pie del sidebar con avatar y logout
function SidebarFooter({ usuario, onLogout }) {
  const initial = (usuario?.nombre || usuario?.email || '?')[0].toUpperCase()
  return (
    <div className="p-2.5 border-t border-white/[0.06]">
      <Link to="/perfil"
        className="flex items-center gap-2.5 p-2 rounded-lg
                   bg-white/[0.02] border border-white/[0.06]
                   hover:bg-white/[0.05] hover:border-white/20 transition">
        <span className="w-8 h-8 rounded-md bg-gradient-ember flex items-center
                         justify-center text-white text-xs font-bold shadow-ember-soft shrink-0">
          {initial}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] text-white truncate font-medium leading-tight">
            {usuario?.nombre || 'Usuario'}
          </p>
          <p className="text-[10px] text-zinc-500 truncate">{usuario?.email}</p>
        </div>
      </Link>
      <button onClick={onLogout}
        className="mt-1.5 w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg
                   text-[11px] text-zinc-400 hover:text-red-300 hover:bg-red-500/10 transition">
        <IconLogout small/> Cerrar sesión
      </button>
    </div>
  )
}

/* ─── Iconos inline con tamaño explícito ─── */
function IconFlame() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="text-white animate-flicker">
      <path d="M12 2c1 3 4 5 4 9a4 4 0 1 1-8 0c0-2 1-3 1-5-2 1-4 4-4 7a7 7 0 1 0 14 0c0-5-4-7-7-11Z"/>
    </svg>
  )
}
function IconDashboard({ className = '' }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <rect x="3" y="3" width="7" height="9" rx="2"/>
      <rect x="14" y="3" width="7" height="5" rx="2"/>
      <rect x="14" y="12" width="7" height="9" rx="2"/>
      <rect x="3" y="16" width="7" height="5" rx="2"/>
    </svg>
  )
}
function IconCamera({ className = '' }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M3 8h3l2-3h8l2 3h3v11H3z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  )
}
function IconAlert({ className = '' }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M10.3 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <circle cx="12" cy="17" r="0.9" fill="currentColor"/>
    </svg>
  )
}
function IconChip({ className = '' }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <rect x="6" y="6" width="12" height="12" rx="2"/>
      <path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>
    </svg>
  )
}
function IconChevron() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-400">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  )
}
function IconUser() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  )
}
function IconLogout({ small }) {
  const s = small ? 12 : 14
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  )
}
function IconMenu() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="3" y1="6" x2="21" y2="6"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
      <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  )
}
function IconX() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  )
}
