import axios from 'axios'
import { API_BASE_URL } from '../constants'

const BACKEND_URL = API_BASE_URL.replace('/api/v1', '')
const PING_INTERVAL = 10 * 60 * 1000

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const sendChatMessage = async (query, sessionId) => {
  const response = await apiClient.post('/chat', { query, session_id: sessionId })
  return response.data
}

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/v1/health`, { timeout: 10000 })
    return response.data?.status === 'ok' || response.data?.status === 'healthy'
  } catch {
    return false
  }
}

export const waitForBackend = async (
  onStatusChange,
  maxAttempts = 10,
  intervalMs = 3000
) => {
  for (let i = 0; i < maxAttempts; i++) {
    onStatusChange('warming_up')
    const isReady = await checkHealth()
    console.log(`Attempt ${i + 1}: isReady = ${isReady}`)  // debug
    if (isReady) {
      console.log('Backend ready! Setting status to ready')  // debug
      onStatusChange('ready')
      return true
    }
    await new Promise(res => setTimeout(res, intervalMs))
  }
  onStatusChange('failed')
  return false
}

// Ping for keep-alive backend 
export const startKeepAlive = () => {
  const ping = async () => {
    try {
      await axios.get(`${BACKEND_URL}/api/v1/health`, { timeout: 5000 })
    } catch {
      // silent fall 
    }
  }

  ping()
  const interval = setInterval(ping, PING_INTERVAL)
  window.addEventListener('beforeunload', () => clearInterval(interval))
  return interval
}