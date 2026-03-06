import Seat   from './Seat'
import Legend from './Legend'

export default function SeatMap({ seats, onSelect, selectedId }) {
  const rows = seats.reduce((acc, seat) => {
    const row = seat.seat_number[0]
    if (!acc[row]) acc[row] = []
    acc[row].push(seat)
    return acc
  }, {})

  return (
    <div>
      <div style={{
        textAlign    : 'center',
        padding      : '10px 48px',
        background   : '#1f2937',
        borderRadius : 8,
        color        : '#6b7280',
        fontSize     : '0.8rem',
        letterSpacing: '0.2em',
        marginBottom : 32,
        border       : '1px solid #374151',
      }}>
        ▬▬▬▬▬▬  STAGE  ▬▬▬▬▬▬
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {Object.entries(rows).map(([row, rowSeats]) => (
          <div key={row} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ width: 20, color: '#4b5563', fontSize: '0.75rem', fontWeight: 700 }}>
              {row}
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              {rowSeats.map(seat => (
                <Seat
                  key={seat.seat_id}
                  seat={seat}
                  selectedId={selectedId}
                  onSelect={onSelect}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      <Legend />
    </div>
  )
}