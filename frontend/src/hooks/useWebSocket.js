import { useEffect, useRef, useState } from 'react'

// Hook para conectarse a un endpoint WebSocket del backend
export function useWebSocket(endpoint) {
  const [datos, setDatos] = useState(null)
  const [conectado, setConectado] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    // No abre conexión si el usuario no está autenticado
    const token = localStorage.getItem('token')
    if (!token) return

    // Abre el WebSocket contra el backend en Railway
    const wsUrl = 'wss://detector-incendios-production.up.railway.app'
    const ws = new WebSocket(`${wsUrl}${endpoint}`)
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
    }

    ws.onerror = (e) => {
      console.error('WebSocket error:', e)
    }

    return () => ws.close()
  }, [endpoint])

  return { datos, conectado }
}