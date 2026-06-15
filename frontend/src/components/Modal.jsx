import { useEffect } from 'react'

// Modal reutilizable: panel afilado con regla brasa, soporte ESC y bloqueo de scroll
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
                    bg-char-950/85 animate-fade-up"
         onClick={onClose}>
      <div
        className={`relative w-full ${sizeClass} bg-char-850 border border-line animate-rise`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Regla brasa superior */}
        <div className="absolute inset-x-0 top-0 h-[3px] bg-fire-grad shadow-ember-glow"/>

        <div className="px-7 pt-7 pb-5 border-b border-line flex items-start justify-between gap-4">
          <div>
            <h2 className="font-display type-expanded font-bold uppercase tracking-wide
                           text-bone text-lg leading-tight">
              {title}
            </h2>
            {subtitle && (
              <p className="font-mono text-[14px] text-ash-400 mt-2 tracking-wide">{subtitle}</p>
            )}
          </div>
          <button onClick={onClose}
            className="p-1.5 -mr-1.5 text-ash-400 hover:text-ember-400 transition-colors"
            aria-label="Cerrar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
                 width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="px-7 py-6">
          {children}
        </div>

        {footer && (
          <div className="px-7 pb-7 pt-1 flex gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
