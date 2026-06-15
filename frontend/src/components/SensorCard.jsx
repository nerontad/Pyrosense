import Counter from './Counter'

// Series por tipo de sensor: color del medidor/valor y rango válido
const SERIES = {
  naranja: { color: '#FF6A26', text: 'text-ember-300', etiqueta: 'Térmico',      range: { min: 0, max: 60 } },
  azul:    { color: '#E0A458', text: 'text-flare-300', etiqueta: 'Hidrométrico', range: { min: 0, max: 100 } },
  verde:   { color: '#97A567', text: 'text-moss-300',  etiqueta: 'Calidad aire', range: { min: 0, max: 2000 } },
  rojo:    { color: '#FF4D00', text: 'text-ember-400', etiqueta: 'Crítico',      range: { min: 0, max: 100 } },
}

// Celda de lectura de un sensor: numeral display + medidor lineal sobre el rango
export default function SensorCard({ titulo, valor, unidad, color = 'azul', estado = 'live' }) {
  const s = SERIES[color] || SERIES.azul
  const v = (valor !== null && valor !== undefined) ? Number(valor) : null
  // Posición del valor dentro del rango [min, max]
  const pct = v !== null
    ? Math.max(0, Math.min(1, (v - s.range.min) / (s.range.max - s.range.min)))
    : 0

  return (
    <div
      className="group bg-char-850 p-6 sm:p-7 transition-colors duration-200 hover:bg-char-800"
      style={{ boxShadow: `inset 0 2px 0 0 ${s.color}59` }}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="kicker">{titulo}</p>
        {estado === 'live' && v !== null && (
          <span className="flex items-center gap-1.5 font-mono text-[13px] uppercase
                           tracking-[0.2em] text-moss-300">
            <span className="dot bg-moss-400 animate-blink"/>
            Vivo
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-2 mt-5">
        {v !== null
          ? <Counter value={v} decimals={1} className={`num-display text-4xl ${s.text}`}/>
          : <span className="num-display text-4xl text-ash-500">——</span>}
        <span className="font-mono text-[15px] text-ash-300">{unidad}</span>
      </div>

      {/* Medidor lineal: posición del valor sobre el rango del sensor */}
      <div className="mt-7">
        <div className="relative h-px bg-line">
          <span
            className="absolute left-0 top-1/2 -translate-y-1/2 h-[3px]
                       transition-[width] duration-700 ease-out-strong"
            style={{
              width: `${pct * 100}%`,
              background: `linear-gradient(90deg, transparent, ${s.color})`,
            }}
          />
          {/* Punta luminosa del medidor */}
          {v !== null && (
            <span
              className="absolute top-1/2 -translate-y-1/2 w-1.5 h-1.5
                         transition-[left] duration-700 ease-out-strong"
              style={{
                left: `calc(${pct * 100}% - 3px)`,
                background: s.color,
                boxShadow: `0 0 10px ${s.color}`,
              }}
            />
          )}
        </div>
        <div className="flex items-baseline justify-between mt-2.5 font-mono text-[13px] text-ash-400">
          <span>{s.range.min}</span>
          <span className="uppercase tracking-[0.2em] text-ash-500 group-hover:text-ash-300 transition-colors duration-200">
            {s.etiqueta}
          </span>
          <span>{s.range.max}</span>
        </div>
      </div>
    </div>
  )
}
