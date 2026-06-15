import { useEffect, useRef, useState } from 'react'

// Numeral animado: cuenta hasta `value` con easing al montar y, cuando `value`
// cambia, interpola suavemente desde el valor actual (ideal para datos en vivo).
// Respeta prefers-reduced-motion (salta directo al valor final).
export default function Counter({
  value,
  decimals = 0,
  duration = 1200,
  prefix = '',
  suffix = '',
  className = '',
}) {
  const [display, setDisplay] = useState(0)
  const curRef = useRef(0)   // último valor mostrado (origen de la interpolación)
  const rafRef = useRef(0)

  useEffect(() => {
    const target = Number(value)
    if (Number.isNaN(target)) return

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      curRef.current = target
      setDisplay(target)
      return
    }

    const from = curRef.current
    const ease = t => 1 - Math.pow(1 - t, 3) // easeOutCubic
    let start = 0
    cancelAnimationFrame(rafRef.current)

    const step = (ts) => {
      if (!start) start = ts
      const p = Math.min(1, (ts - start) / duration)
      const v = from + (target - from) * ease(p)
      curRef.current = v
      setDisplay(v)
      if (p < 1) rafRef.current = requestAnimationFrame(step)
      else curRef.current = target
    }
    rafRef.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(rafRef.current)
  }, [value, duration])

  return (
    <span className={className}>
      {prefix}{display.toFixed(decimals)}{suffix}
    </span>
  )
}
