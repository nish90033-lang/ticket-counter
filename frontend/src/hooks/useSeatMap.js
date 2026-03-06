import { useState, useEffect, useCallback } from 'react'
import { fetchSeats } from '../api/client'

export function useSeatMap(eventId) {
  const [seats,   setSeats]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const load = useCallback(async () => {
    try {
      const { data } = await fetchSeats(eventId)
      setSeats(data.seats)
      setError(null)
    } catch (e) {
      setError('Failed to load seat map.')
    } finally {
      setLoading(false)
    }
  }, [eventId])

  useEffect(() => {
    load()
    const interval = setInterval(load, 10_000)
    return () => clearInterval(interval)
  }, [load])

  return { seats, loading, error, refresh: load }
}