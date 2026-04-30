export default function AlertaBadge({ clase, confianza }) {
  const esIncendio = clase === 'fire' || clase === 'incendio'

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
      esIncendio
        ? 'bg-red-900/60 text-red-300 border border-red-600'
        : 'bg-yellow-900/60 text-yellow-300 border border-yellow-600'
    }`}>
      {esIncendio ? '🔥' : '💨'}
      {clase} — {(confianza * 100).toFixed(0)}%
    </span>
  )
}