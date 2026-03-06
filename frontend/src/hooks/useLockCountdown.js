import { useState, useEffect } from 'react'

export function useLockCountdown(secondsRemaining, onExpire) {
  const [seconds, setSeconds] = useState(secondsRemaining ?? 0)

  useEffect(() => {
    setSeconds(secondsRemaining ?? 0)
  }, [secondsRemaining])

  useEffect(() => {
    if (seconds <= 0) {
      onExpire?.()
      return
    }
    const timer = setInterval(() => {
      setSeconds((s) => {
        if (s <= 1) { onExpire?.(); return 0 }
        return s - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [seconds])

  const mm = String(Math.floor(seconds / 60)).padStart(2, '0')
  const ss = String(seconds % 60).padStart(2, '0')
  return `${mm}:${ss}`
}