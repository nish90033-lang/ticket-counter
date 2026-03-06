export default function Seat({ seat, onSelect, selectedId }) {
  const isSelected  = selectedId === seat.seat_id
  const isAvailable = seat.status === 'available'
  const isLocked    = seat.status === 'locked'
  const isReserved  = seat.status === 'reserved'

  const base = {
    width          : 40,
    height         : 40,
    borderRadius   : 8,
    display        : 'flex',
    alignItems     : 'center',
    justifyContent : 'center',
    fontSize       : '0.65rem',
    fontWeight     : 700,
    cursor         : isAvailable ? 'pointer' : 'not-allowed',
    transition     : 'all 0.15s ease',
    border         : '2px solid transparent',
    userSelect     : 'none',
  }

  const styles = {
    available : { ...base, background: '#1a2e1a', color: '#4ade80', borderColor: '#4ade80' },
    locked    : { ...base, background: '#2e2a1a', color: '#f59e0b', borderColor: '#f59e0b' },
    reserved  : { ...base, background: '#1f1f1f', color: '#4b5563', borderColor: '#374151' },
    selected  : { ...base, background: '#4ade80', color: '#000',    borderColor: '#4ade80',
                  transform: 'scale(1.15)', boxShadow: '0 0 16px #4ade8088' },
  }

  const style = isSelected  ? styles.selected
              : isAvailable ? styles.available
              : isLocked    ? styles.locked
              : styles.reserved

  const label = isReserved ? '✕'
              : isLocked   ? '🔒'
              : seat.seat_number

  return (
    <div
      style={style}
      title={
        isReserved  ? 'Already booked'
        : isLocked  ? `Held — ${seat.seconds_remaining}s remaining`
        : `Seat ${seat.seat_number} — click to select`
      }
      onClick={() => isAvailable && onSelect(seat)}
    >
      {label}
    </div>
  )
}