import { useState }  from 'react'
import { lockSeat }  from '../../api/client'
import Countdown     from '../UI/Countdown'

export default function LockStep({ seat, onLocked, onCancel }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  const [lock,    setLock]    = useState(null)

  async function handleLock() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await lockSeat(seat.seat_id)
      setLock(data)
      onLocked(data)
    } catch (e) {
      setError(e.response?.data?.error ?? 'Failed to lock seat.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={panel}>
      <h3 style={{ color: '#f9fafb', marginBottom: 8 }}>
        Reserve Seat <span style={{ color: '#4ade80' }}>{seat.seat_number}</span>
      </h3>
      <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: 24 }}>
        Locking this seat gives you 5 minutes to complete payment.
        The seat is released if you don't finish in time.
      </p>

      {error && <div style={errorBox}>{error}</div>}

      {lock ? (
        <div style={{ color: '#4ade80' }}>
          ✅ Seat locked! Time remaining:&nbsp;
          <Countdown seconds={lock.seconds_remaining} onExpire={onCancel} />
        </div>
      ) : (
        <div style={{ display: 'flex', gap: 12 }}>
          <button style={btnPrimary} onClick={handleLock} disabled={loading}>
            {loading ? 'Locking…' : '🔒 Lock Seat'}
          </button>
          <button style={btnGhost} onClick={onCancel}>
            Cancel
          </button>
        </div>
      )}
    </div>
  )
}

const panel      = { background: '#111827', border: '1px solid #1f2937', borderRadius: 12, padding: 24 }
const errorBox   = { background: '#450a0a', border: '1px solid #991b1b', borderRadius: 8,
                     color: '#fca5a5', padding: '10px 14px', marginBottom: 16, fontSize: '0.85rem' }
const btnPrimary = { background: '#4ade80', color: '#000', border: 'none', borderRadius: 8,
                     padding: '10px 20px', fontWeight: 700, cursor: 'pointer', fontSize: '0.9rem' }
const btnGhost   = { background: 'transparent', color: '#6b7280', border: '1px solid #374151',
                     borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontSize: '0.9rem' }