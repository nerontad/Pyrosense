import Navbar from './Navbar'

// Layout de páginas internas: spine + cabecera editorial con índice y título display.
// El título usa clamp() para escalar fluido sin desbordar en móvil.
export default function PageShell({ index = '00', title, subtitle, actions, children, max = 'max-w-[1400px]' }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="lg:pl-[76px]">
        <div className={`${max} mx-auto px-5 sm:px-10 lg:px-16 pt-10 lg:pt-16 pb-24`}>
          {title && (
            <header className="mb-10 lg:mb-16 animate-rise">
              <div className="flex items-end justify-between flex-wrap gap-x-8 gap-y-6">
                <div>
                  <p className="kicker mb-4">
                    <span className="text-ash-500">[</span>
                    <span className="text-ember-400 mx-2">{index}</span>
                    <span className="text-ash-500">/</span>
                    <span className="mx-2">Pyrosense</span>
                    <span className="text-ash-500">]</span>
                  </p>
                  <h1 className="font-display type-expanded font-black uppercase text-bone
                                 leading-[0.95] tracking-[-0.02em]
                                 text-[clamp(1.9rem,4.5vw,3.4rem)]">
                    {title}
                  </h1>
                  {subtitle && (
                    <p className="font-mono text-[15px] text-ash-300 mt-4 tracking-wide max-w-xl">
                      <span className="text-ember-500 mr-2">//</span>
                      {subtitle}
                    </p>
                  )}
                </div>
                {actions && (
                  <div className="flex flex-wrap items-center gap-3 pb-1">
                    {actions}
                  </div>
                )}
              </div>
              {/* Regla que se enciende: brasa a la izquierda, se apaga hacia la derecha */}
              <div className="mt-8 lg:mt-12 h-px bg-gradient-to-r from-ember-500/70 via-line to-transparent"/>
            </header>
          )}
          {children}
        </div>
      </main>
    </div>
  )
}
