import { useLockCountdown } from '../../hooks/useLockCountdown'

export default function Countdown({ seconds, onExpire }) {
  const display  = useLockCountdown(seconds, onExpire)
  const isUrgent = seconds <= 60

  return (
    <span style={{
      fontFamily : 'monospace',
      fontSize   : '1.1rem',
      fontWeight : 700,
      color      : isUrgent ? '#ef4444' : '#f59e0b',
      animation  : isUrgent ? 'pulse 1s infinite' : 'none',
    }}>
      ⏱ {display}
    </span>
  )
}