// Badge con el tipo y confianza de una alerta detectada
export default function AlertaBadge({ clase, confianza }) {
  const esIncendio = clase === 'fire' || clase === 'incendio'
  const pct = (confianza * 100).toFixed(0)
  const severo = confianza >= 0.85

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
                      text-[11px] font-semibold border
                      ${esIncendio
                        ? 'bg-red-500/15 text-red-300 border-red-500/40'
                        : 'bg-amber-500/15 text-amber-300 border-amber-500/40'}
                      ${severo ? 'shadow-[0_0_18px_rgba(239,68,68,0.35)]' : ''}`}>
      <span className={`text-sm ${esIncendio ? 'animate-flicker' : ''}`}>
        {esIncendio ? '🔥' : '💨'}
      </span>
      <span className="capitalize">{clase}</span>
      <span className="opacity-50">·</span>
      <span className="tabular-nums">{pct}%</span>
    </span>
  )
}
