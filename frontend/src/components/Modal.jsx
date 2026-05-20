import { useEffect } from 'react'

// Modal reutilizable con backdrop, soporte ESC y bloqueo de scroll
export default function Modal({ open, onClose, title, subtitle, children, footer, size = 'md' }) {
  // Cierra con ESC y bloquea el scroll del body mientras está abierto
  useEffect(() => {
    if (!open) return
    const onKey = (e) => { if (e.key === 'Escape') onClose?.() }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  const sizeClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
  }[size] || 'max-w-md'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4
                    bg-ink-950/70 backdrop-blur-sm animate-fade-in-up"
         onClick={onClose}>
      <div
        className={`relative w-full ${sizeClass} panel shadow-glass-lg
                    overflow-hidden`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* hairline ember en el borde superior */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r
                        from-transparent via-ember-500/60 to-transparent"/>

        <div className="px-6 pt-5 pb-4 border-b border-white/[0.06] flex items-start justify-between gap-3">
          <div>
            <h2 className="text-white font-display font-semibold text-lg tracking-tight">{title}</h2>
            {subtitle && <p className="text-zinc-400 text-sm mt-1">{subtitle}</p>}
          </div>
          <button onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition"
            aria-label="Cerrar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                 strokeLinecap="round" width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div className="px-6 py-5">
          {children}
        </div>
        {footer && (
          <div className="px-6 pb-5 pt-1 flex gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
