import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

const link = document.createElement('link')
link.rel  = 'stylesheet'
link.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap'
document.head.appendChild(link)

createRoot(document.getElementById('root')).render(
  <StrictMode><App /></StrictMode>
)