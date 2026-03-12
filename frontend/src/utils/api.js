import axios from 'axios'
import { API_BASE_URL } from '../constants'

// Axios instance dengan base config
// semua request otomatis pakai base URL dan timeout ini
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 detik — LLM inference bisa lama
  headers: {
    'Content-Type': 'application/json'
  }
})

export const sendChatMessage = async (query) => {
  const response = await apiClient.post('/chat', { query })
  return response.data
}

export const checkHealth = async () => {
  const response = await apiClient.get('/health')
  return response.data
}