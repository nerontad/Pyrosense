// Tag con el tipo de detección y su nivel de confianza
export default function AlertaBadge({ clase, confianza }) {
  const esIncendio = clase === 'fire' || clase === 'incendio'
  const pct = (confianza * 100).toFixed(0)

  return (
    <span className={`tag ${esIncendio ? 'tag-ember' : 'tag-flare'}`}>
      <span className={`dot ${esIncendio ? 'bg-ember-500 animate-blink' : 'bg-flare-400'}`}/>
      {esIncendio ? 'Fuego' : 'Humo'}
      <span className="text-ash-500">·</span>
      <span className="tabular-nums">{pct}%</span>
      {/* Mini barra de confianza */}
      <span className="relative inline-block w-10 h-px bg-line ml-1">
        <span
          className="absolute left-0 top-0 h-full"
          style={{
            width: `${pct}%`,
            background: esIncendio ? '#FF4D00' : '#E0A458',
          }}
        />
      </span>
    </span>
  )
}
