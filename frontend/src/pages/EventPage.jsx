import { useState }    from 'react'
import { useSeatMap }  from '../hooks/useSeatMap'
import { releaseLock } from '../api/client'
import SeatMap         from '../components/SeatMap/SeatMap'
import LockStep        from '../components/BookingFlow/LockStep'
import PaymentStep     from '../components/BookingFlow/PaymentStep'
import ConfirmStep     from '../components/BookingFlow/ConfirmStep'

const STEP = { IDLE: 'idle', LOCKING: 'locking', PAYMENT: 'payment', CONFIRMED: 'confirmed' }

export default function EventPage({ eventId = 1 }) {
  const { seats, loading, error, refresh } = useSeatMap(eventId)

  const [step,         setStep]         = useState(STEP.IDLE)
  const [selectedSeat, setSelectedSeat] = useState(null)
  const [lockData,     setLockData]     = useState(null)
  const [bookingData,  setBookingData]  = useState(null)

  function handleSeatSelect(seat) {
    setSelectedSeat(seat)
    setStep(STEP.LOCKING)
  }

  function handleLocked(lock) {
    setLockData(lock)
    setStep(STEP.PAYMENT)
  }

  async function handleCancel() {
    if (selectedSeat) {
      try { await releaseLock(selectedSeat.seat_id) } catch (_) {}
    }
    setStep(STEP.IDLE)
    setSelectedSeat(null)
    setLockData(null)
    refresh()
  }

  function handleConfirmed(booking) {
    setBookingData(booking)
    setStep(STEP.CONFIRMED)
    refresh()
  }

  return (
    <div style={page}>

      {/* Header */}
      <header style={header}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
          <span style={{ fontSize: '1.4rem' }}>🎟️</span>
          <h1 style={{ color: '#f9fafb', fontSize: '1.3rem', fontWeight: 800, margin: 0 }}>
            TicketCounter
          </h1>
        </div>
        <span style={{ color: '#6b7280', fontSize: '0.8rem' }}>
          Seat map updates every 10s
        </span>
      </header>

      <main style={main}>

        {/* Left — Seat map */}
        <section style={leftPane}>
          <h2 style={{ color: '#f9fafb', fontSize: '1rem', marginBottom: 20, fontWeight: 700 }}>
            Select a Seat
          </h2>

          {loading && <p style={{ color: '#4b5563' }}>Loading seat map…</p>}
          {error   && <p style={{ color: '#ef4444' }}>{error}</p>}

          {!loading && !error && (
            <SeatMap
              seats={seats}
              selectedId={selectedSeat?.seat_id}
              onSelect={handleSeatSelect}
            />
          )}
        </section>

        {/* Right — Booking flow */}
        <section style={rightPane}>
          {step === STEP.IDLE && (
            <div style={placeholder}>
              <div style={{ fontSize: '2rem', marginBottom: 12 }}>👆</div>
              <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                Select an available seat to begin booking
              </p>
            </div>
          )}

          {step === STEP.LOCKING && (
            <LockStep
              seat={selectedSeat}
              onLocked={handleLocked}
              onCancel={handleCancel}
            />
          )}

          {step === STEP.PAYMENT && (
            <PaymentStep
              seat={selectedSeat}
              lock={lockData}
              onConfirmed={handleConfirmed}
              onExpire={handleCancel}
            />
          )}

          {step === STEP.CONFIRMED && (
            <ConfirmStep
              booking={bookingData}
              seat={selectedSeat}
            />
          )}
        </section>

      </main>
    </div>
  )
}

const page = {
  minHeight  : '100vh',
  background : '#0d1117',
  fontFamily : "'IBM Plex Mono', monospace",
  color      : '#f9fafb',
}
const header = {
  display        : 'flex',
  justifyContent : 'space-between',
  alignItems     : 'center',
  padding        : '16px 32px',
  borderBottom   : '1px solid #1f2937',
  background     : '#0d1117',
  position       : 'sticky',
  top            : 0,
  zIndex         : 10,
}
const main = {
  display             : 'grid',
  gridTemplateColumns : '1fr 380px',
  gap                 : 32,
  padding             : '32px',
  maxWidth            : 1200,
  margin              : '0 auto',
}
const leftPane    = { overflowX: 'auto' }
const rightPane   = { position: 'sticky', top: 80, alignSelf: 'start' }
const placeholder = {
  border       : '1px dashed #1f2937',
  borderRadius : 12,
  padding      : 48,
  textAlign    : 'center',
}

