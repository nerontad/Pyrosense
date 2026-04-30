export default function SensorCard({ titulo, valor, unidad, icono, color }) {
  const colores = {
    naranja: 'border-orange-500 bg-orange-500/10',
    azul:    'border-blue-500 bg-blue-500/10',
    verde:   'border-green-500 bg-green-500/10',
    rojo:    'border-red-500 bg-red-500/10',
  }

  return (
    <div className={`border-2 rounded-xl p-5 ${colores[color] || colores.azul}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{titulo}</span>
        <span className="text-2xl">{icono}</span>
      </div>
      <div className="flex items-end gap-1">
        <span className="text-white text-3xl font-bold">
          {valor !== null && valor !== undefined ? Number(valor).toFixed(1) : '--'}
        </span>
        <span className="text-gray-400 text-sm mb-1">{unidad}</span>
      </div>
    </div>
  )
}