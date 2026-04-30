import { useEffect, useRef, useState } from 'react'

export function useWebSocket(endpoint) {
  const [datos, setDatos] = useState(null)
  const [conectado, setConectado] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return

    const ws = new WebSocket(`ws://127.0.0.1:8000${endpoint}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConectado(true)
      console.log(`WebSocket conectado: ${endpoint}`)
    }

    ws.onmessage = (e) => {
      try {
        setDatos(JSON.parse(e.data))
      } catch {
        console.error('Error parseando mensaje WS')
      }
    }

    ws.onclose = () => {
      setConectado(false)
      console.log(`WebSocket desconectado: ${endpoint}`)
    }

    ws.onerror = (e) => {
      console.error('WebSocket error:', e)
    }

    return () => ws.close()
  }, [endpoint])

  return { datos, conectado }
}