import { useState }       from 'react'
import { confirmBooking } from '../../api/client'
import Countdown          from '../UI/Countdown'

export default function PaymentStep({ seat, lock, onConfirmed, onExpire }) {
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function handlePay() {
    setLoading(true)
    setError(null)
    try {
      const fakePaymentRef = `PAY-${Date.now()}`
      const { data }       = await confirmBooking(seat.seat_id, fakePaymentRef)
      onConfirmed(data)
    } catch (e) {
      const status = e.response?.status
      if (status === 410) {
        setError('Your seat hold expired. Please start over.')
        onExpire()
      } else {
        setError(e.response?.data?.error ?? 'Payment failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={panel}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h3 style={{ color: '#f9fafb', margin: 0 }}>Payment</h3>
        <Countdown seconds={lock.seconds_remaining} onExpire={onExpire} />
      </div>

      <div style={summaryBox}>
        <div style={row}><span>Seat</span>       <strong>{seat.seat_number}</strong></div>
        <div style={row}><span>Booking ref</span><strong style={{ color: '#4ade80' }}>Pending</strong></div>
      </div>

      <div style={cardMock}>
        <span style={{ color: '#4b5563', fontSize: '0.85rem' }}>
          💳 &nbsp;Stripe Elements placeholder
        </span>
      </div>

      {error && <div style={errorBox}>{error}</div>}

      <button style={btnPrimary} onClick={handlePay} disabled={loading}>
        {loading ? 'Processing…' : 'Pay & Confirm Booking'}
      </button>
    </div>
  )
}

const panel      = { background: '#111827', border: '1px solid #1f2937', borderRadius: 12, padding: 24 }
const summaryBox = { background: '#0d1117', borderRadius: 8, padding: '12px 16px', marginBottom: 20 }
const row        = { display: 'flex', justifyContent: 'space-between', color: '#9ca3af',
                     fontSize: '0.85rem', padding: '4px 0' }
const cardMock   = { border: '1px dashed #374151', borderRadius: 8, padding: 20,
                     textAlign: 'center', marginBottom: 20 }
const errorBox   = { background: '#450a0a', border: '1px solid #991b1b', borderRadius: 8,
                     color: '#fca5a5', padding: '10px 14px', marginBottom: 16, fontSize: '0.85rem' }
const btnPrimary = { background: '#4ade80', color: '#000', border: 'none', borderRadius: 8,
                     padding: '12px 24px', fontWeight: 700, cursor: 'pointer',
                     fontSize: '0.95rem', width: '100%' }