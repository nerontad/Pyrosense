// Paletas y rangos válidos por tipo de sensor
const PALETAS = {
  naranja: {
    text:  'text-ember-300',
    glow:  'from-ember-500/30 to-ember-700/0',
    ring:  'stroke-ember-400',
    track: 'stroke-ember-500/15',
    badge: 'bg-ember-500/15 border-ember-500/30 text-ember-300',
    range: { min: 0, max: 60 },
  },
  azul: {
    text:  'text-sky-300',
    glow:  'from-sky-500/30 to-sky-700/0',
    ring:  'stroke-sky-400',
    track: 'stroke-sky-500/15',
    badge: 'bg-sky-500/15 border-sky-500/30 text-sky-300',
    range: { min: 0, max: 100 },
  },
  verde: {
    text:  'text-emerald-300',
    glow:  'from-emerald-500/25 to-emerald-700/0',
    ring:  'stroke-emerald-400',
    track: 'stroke-emerald-500/15',
    badge: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300',
    range: { min: 0, max: 2000 },
  },
  rojo: {
    text:  'text-red-300',
    glow:  'from-red-500/30 to-red-700/0',
    ring:  'stroke-red-400',
    track: 'stroke-red-500/15',
    badge: 'bg-red-500/15 border-red-500/30 text-red-300',
    range: { min: 0, max: 100 },
  },
}

// Tarjeta de lectura de un sensor con anillo de progreso
export default function SensorCard({ titulo, valor, unidad, icono, color = 'azul', estado = 'live' }) {
  const p = PALETAS[color] || PALETAS.azul
  const v = (valor !== null && valor !== undefined) ? Number(valor) : null
  // Calcula el porcentaje del valor dentro del rango [min, max]
  const pct = v !== null
    ? Math.max(0, Math.min(1, (v - p.range.min) / (p.range.max - p.range.min)))
    : 0

  // Cálculo del anillo SVG (radio, perímetro y offset del trazo)
  const R = 28
  const C = 2 * Math.PI * R
  const offset = C * (1 - pct)

  return (
    <div className="group relative overflow-hidden panel panel-hover p-5">
      {/* glow */}
      <div className={`pointer-events-none absolute -top-16 -right-16 w-40 h-40 rounded-full
                       bg-gradient-radial blur-2xl opacity-70 bg-gradient-to-br ${p.glow}`}/>
      <div className="absolute inset-0 bg-grid opacity-[0.04]"/>

      <div className="relative flex items-start justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-[0.18em] text-zinc-500 font-medium">
            {titulo}
          </p>
          <div className="flex items-baseline gap-1.5 mt-2">
            <span className="text-4xl font-display font-bold text-white tabular-nums">
              {v !== null ? v.toFixed(1) : '—'}
            </span>
            <span className="text-zinc-400 text-sm">{unidad}</span>
          </div>
          <div className="flex items-center gap-2 mt-3">
            <span className={`chip ${p.badge}`}>{icono} {color === 'naranja' ? 'Térmico' : color === 'azul' ? 'Hidro' : 'Calidad aire'}</span>
            {estado === 'live' && v !== null && (
              <span className="text-[11px] text-zinc-500 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft"/>
                live
              </span>
            )}
          </div>
        </div>

        {/* Anillo circular SVG con el avance del valor */}
        <div className="relative">
          <svg width="72" height="72" viewBox="0 0 72 72" className="-rotate-90">
            <circle cx="36" cy="36" r={R} className={p.track} fill="none" strokeWidth="6" strokeLinecap="round"/>
            <circle
              cx="36" cy="36" r={R}
              className={`${p.ring} transition-[stroke-dashoffset] duration-700 ease-out`}
              fill="none" strokeWidth="6" strokeLinecap="round"
              strokeDasharray={C}
              strokeDashoffset={offset}
              style={{ filter: 'drop-shadow(0 0 6px currentColor)' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-xl">
            {icono}
          </div>
        </div>
      </div>
    </div>
  )
}
