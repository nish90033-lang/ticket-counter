import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const fetchSeats     = (eventId)             => api.get(`/events/${eventId}/seats/`)
export const lockSeat       = (seatId)              => api.post(`/seats/${seatId}/lock/`)
export const releaseLock    = (seatId)              => api.delete(`/seats/${seatId}/lock/release/`)
export const confirmBooking = (seatId, paymentRef)  => api.post(`/seats/${seatId}/confirm/`, { payment_ref: paymentRef })

export default api