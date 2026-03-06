export default function Toast({ message, type = 'error' }) {
  if (!message) return null

  const colors = {
    error   : { bg: '#450a0a', border: '#991b1b', text: '#fca5a5' },
    success : { bg: '#052e16', border: '#166534', text: '#86efac' },
    info    : { bg: '#0c1a2e', border: '#1e3a5f', text: '#93c5fd' },
  }

  const c = colors[type] ?? colors.error

  return (
    <div style={{
      background   : c.bg,
      border       : `1px solid ${c.border}`,
      borderRadius : 8,
      color        : c.text,
      padding      : '10px 14px',
      fontSize     : '0.85rem',
      marginBottom : 16,
    }}>
      {message}
    </div>
  )
}