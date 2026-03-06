export default function Spinner() {
  return (
    <div style={{
      width        : 32,
      height       : 32,
      border       : '3px solid #1f2937',
      borderTop    : '3px solid #4ade80',
      borderRadius : '50%',
      animation    : 'spin 0.8s linear infinite',
    }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}