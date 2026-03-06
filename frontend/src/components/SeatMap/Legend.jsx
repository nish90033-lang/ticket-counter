export default function Legend() {
  const items = [
    { color: '#4ade80', label: 'Available' },
    { color: '#f59e0b', label: 'Locked'    },
    { color: '#374151', label: 'Reserved'  },
  ]
  return (
    <div style={{ display: 'flex', gap: 24, marginTop: 24 }}>
      {items.map(({ color, label }) => (
        <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 16, height: 16, borderRadius: 4,
            background: color, border: `2px solid ${color}`
          }} />
          <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{label}</span>
        </div>
      ))}
    </div>
  )
}