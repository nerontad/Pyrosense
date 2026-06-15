import Counter from './Counter'

// Layout de las páginas de autenticación: póster tipográfico + formulario sin caja
export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-12">
      {/* Panel izquierdo: póster técnico de la marca */}
      <aside className="hidden lg:flex lg:col-span-5 xl:col-span-6 relative overflow-hidden
                        border-r border-line bg-char-950">
        {/* Calor ambiental del póster */}
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: 'radial-gradient(85% 70% at 15% 100%, rgba(255,77,0,0.14), transparent 60%)' }}/>
        {/* Ghost type de fondo */}
        <span aria-hidden
          className="absolute -bottom-10 -right-6 font-display font-black uppercase select-none
                     pointer-events-none text-outline-ember leading-none animate-flicker"
          style={{ fontSize: '13rem', fontStretch: '125%' }}>
          PYRO
        </span>

        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16 w-full">
          {/* Marca */}
          <div className="flex items-center gap-4">
            <span className="text-ember-500 animate-flicker">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2c1 3 4 5 4 9a4 4 0 1 1-8 0c0-2 1-3 1-5-2 1-4 4-4 7a7 7 0 1 0 14 0c0-5-4-7-7-11Z"/>
              </svg>
            </span>
            <span className="font-mono text-[14px] uppercase tracking-mega text-bone">
              Pyrosense
            </span>
          </div>

          {/* Declaración tipográfica */}
          <div className="max-w-xl animate-rise">
            <h2 className="font-display type-expanded font-black uppercase text-bone
                           text-[clamp(2.4rem,4vw,3.6rem)] leading-[0.92] tracking-[-0.02em]">
              Ver el <span className="text-fire glow-ember">fuego</span><br/>
              antes que<br/>
              se propague.
            </h2>
            <p className="font-mono text-[15px] text-ash-300 mt-7 leading-relaxed max-w-sm">
              Visión artificial sobre cámaras IP, sensores ambientales distribuidos
              y alertas en tiempo real. Vigilancia continua, 24/7.
            </p>

            {/* Telemetría del sistema como registro */}
            <div className="mt-10 border-t border-b border-line divide-y divide-line stagger">
              {[
                { k: 'Latencia de detección', num: 2,    dec: 0, prefix: '< ', suffix: ' s', c: 'text-ember-300' },
                { k: 'Precisión del modelo',  num: 90,   dec: 0, suffix: ' %', c: 'text-flare-300' },
                { k: 'Disponibilidad',        num: 99.9, dec: 1, suffix: ' %', c: 'text-moss-300' },
              ].map(s => (
                <div key={s.k} className="flex items-baseline justify-between py-4">
                  <span className="kicker">{s.k}</span>
                  <Counter
                    value={s.num} decimals={s.dec} prefix={s.prefix} suffix={s.suffix}
                    className={`num-display text-2xl ${s.c}`}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Pie con coordenadas */}
          <p className="font-mono text-[13px] uppercase tracking-[0.2em] text-ash-500">
            35.4264° S · 71.6554° W — Región del Maule, CL · © {new Date().getFullYear()}
          </p>
        </div>
      </aside>

      {/* Panel derecho: formulario alineado a la izquierda, sin tarjeta */}
      <section className="lg:col-span-7 xl:col-span-6 flex flex-col justify-center
                          px-6 sm:px-16 xl:px-24 py-14 lg:py-20">
        <div className="w-full max-w-md">
          {/* Marca en móvil */}
          <div className="lg:hidden flex items-center gap-3 mb-14 text-ember-500">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2c1 3 4 5 4 9a4 4 0 1 1-8 0c0-2 1-3 1-5-2 1-4 4-4 7a7 7 0 1 0 14 0c0-5-4-7-7-11Z"/>
            </svg>
            <span className="font-mono text-[13px] uppercase tracking-mega text-bone">
              Pyrosense
            </span>
          </div>

          <div className="animate-rise">
            {subtitle && (
              <p className="kicker mb-4">
                <span className="text-ember-500 mr-2">//</span>
                {subtitle}
              </p>
            )}
            <h1 className="font-display type-expanded font-black uppercase text-bone
                           text-[clamp(2rem,5vw,3rem)] leading-[0.95] tracking-[-0.02em]">
              {title}
            </h1>

            <div className="mt-10">
              {children}
            </div>

            {footer && (
              <div className="mt-10 pt-6 border-t border-line font-mono text-xs">
                {footer}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
