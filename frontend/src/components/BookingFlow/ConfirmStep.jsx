export default function ConfirmStep({ booking, seat }) {
  return (
    <div style={{ ...panel, textAlign: 'center' }}>
      <div style={{ fontSize: '3rem', marginBottom: 16 }}>🎟️</div>
      <h2 style={{ color: '#4ade80', marginBottom: 8 }}>Booking Confirmed!</h2>
      <p style={{ color: '#9ca3af', marginBottom: 24 }}>
        Your seat has been secured. Check your email for the ticket.
      </p>

      <div style={refBox}>
        <div style={{ color: '#6b7280', fontSize: '0.75rem', letterSpacing: '0.1em', marginBottom: 4 }}>
          BOOKING REFERENCE
        </div>
        <div style={{ color: '#f9fafb', fontSize: '1.4rem', fontFamily: 'monospace', fontWeight: 700 }}>
          {booking.booking_ref}
        </div>
      </div>

      <div style={detailsGrid}>
        <Detail label="Seat"      value={seat.seat_number} />
        <Detail label="Status"    value="✅ Confirmed"     />
        <Detail label="Confirmed" value={new Date(booking.confirmed_at).toLocaleString()} />
      </div>
    </div>
  )
}

function Detail({ label, value }) {
  return (
    <div style={{ textAlign: 'left' }}>
      <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: 2 }}>{label}</div>
      <div style={{ color: '#f9fafb', fontWeight: 600 }}>{value}</div>
    </div>
  )
}

const panel       = { background: '#111827', border: '1px solid #1f2937', borderRadius: 12, padding: 32 }
const refBox      = { background: '#0d1117', border: '1px solid #4ade8033', borderRadius: 10,
                      padding: '16px 24px', marginBottom: 24, display: 'inline-block' }
const detailsGrid = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, textAlign: 'left', marginTop: 8 }