// Layout de las páginas de autenticación (split-screen con hero + formulario)
export default function AuthShell({ title, subtitle, icon = '🔥', children, footer }) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2 relative overflow-hidden">
      {/* Panel izquierdo: hero animado con la marca */}
      <aside className="hidden lg:flex relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-ember-700 via-red-800 to-ink-950"/>
        <div className="absolute inset-0 bg-grid opacity-30"/>
        {/* Partículas tipo brasas que flotan */}
        {[...Array(14)].map((_, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-ember-300/70 blur-[1px] animate-float-slow"
            style={{
              left:  `${(i * 73) % 100}%`,
              top:   `${(i * 37) % 100}%`,
              width:  `${4 + (i % 4) * 2}px`,
              height: `${4 + (i % 4) * 2}px`,
              animationDelay:    `${(i * 0.4).toFixed(1)}s`,
              animationDuration: `${6 + (i % 5)}s`,
              boxShadow: '0 0 14px rgba(255,140,60,0.7)',
            }}
          />
        ))}
        {/* Glow grande */}
        <div className="absolute -bottom-40 -left-40 w-[520px] h-[520px] rounded-full
                        bg-ember-500/30 blur-3xl"/>
        <div className="absolute -top-40 -right-40 w-[420px] h-[420px] rounded-full
                        bg-red-600/25 blur-3xl"/>

        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <div className="flex items-center gap-3">
            <span className="flex items-center justify-center w-11 h-11 rounded-xl
                             bg-white/10 backdrop-blur border border-white/20">
              <span className="text-2xl">🔥</span>
            </span>
            <div>
              <p className="font-display font-bold text-white text-lg leading-none">Pyrosense</p>
              <p className="text-[11px] text-white/70 uppercase tracking-[0.25em] mt-1">
                Fire Watch System
              </p>
            </div>
          </div>

          <div className="space-y-5 max-w-md">
            <h2 className="font-display text-4xl xl:text-5xl font-bold text-white leading-tight">
              Detecta el fuego <br/>
              <span className="text-shadow-ember">antes</span> que se propague.
            </h2>
            <p className="text-white/80 text-sm leading-relaxed">
              Visión artificial, sensores IoT y alertas en tiempo real. Una capa de
              vigilancia continua para tu infraestructura, 24/7.
            </p>
            <div className="grid grid-cols-3 gap-3 pt-4">
              {[
                { k: 'Latencia', v: '<2s' },
                { k: 'Detección', v: '94%' },
                { k: 'Uptime',   v: '99.9%' },
              ].map(s => (
                <div key={s.k} className="rounded-xl bg-white/10 backdrop-blur
                                          border border-white/15 px-3 py-3">
                  <p className="text-2xl font-bold text-white">{s.v}</p>
                  <p className="text-[10px] uppercase tracking-wider text-white/70">{s.k}</p>
                </div>
              ))}
            </div>
          </div>

          <p className="text-xs text-white/60">
            Región del Maule · © {new Date().getFullYear()} Pyrosense
          </p>
        </div>
      </aside>

      {/* Panel derecho: contenido del formulario */}
      <section className="relative flex items-center justify-center px-4 py-10 lg:py-12">
        <div className="absolute inset-0 lg:hidden bg-radial-ember pointer-events-none"/>
        <div className="relative w-full max-w-md">
          <div className="text-center mb-7">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl
                            bg-gradient-ember shadow-ember mb-4 animate-flicker">
              <span className="text-2xl">{icon}</span>
            </div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-white tracking-tight">
              {title}
            </h1>
            {subtitle && (
              <p className="text-zinc-400 text-sm mt-2">{subtitle}</p>
            )}
          </div>

          <div className="panel p-6 sm:p-7 animate-fade-in-up">
            {children}
          </div>

          {footer && (
            <div className="text-center text-sm mt-5">
              {footer}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
