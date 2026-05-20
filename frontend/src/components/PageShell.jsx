import Navbar from './Navbar'

// Layout estándar de páginas internas: sidebar + título + contenido
export default function PageShell({ title, subtitle, actions, children, max = 'max-w-7xl' }) {
  return (
    <div className="min-h-screen relative">
      <Navbar />
      <main className="lg:pl-56">
        <div className={`${max} mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8`}>
          {(title || actions) && (
            <header className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
              <div>
                {title && (
                  <h1 className="font-display text-2xl sm:text-3xl font-bold text-white tracking-tight">
                    {title}
                  </h1>
                )}
                {subtitle && (
                  <p className="text-sm text-zinc-400 mt-1.5">{subtitle}</p>
                )}
              </div>
              {actions && (
                <div className="flex flex-wrap items-center gap-2">
                  {actions}
                </div>
              )}
            </header>
          )}
          {children}
        </div>
      </main>
    </div>
  )
}
