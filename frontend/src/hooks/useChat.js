import { useState, useCallback, useEffect } from 'react'
import { sendChatMessage } from '../utils/api'

const SESSION_KEY = 'nutriguide_messages'
const SESSION_ID_KEY = 'nutriguide_session_id'

const loadMessages = () => {
  try {
    const saved = sessionStorage.getItem(SESSION_KEY)
    return saved ? JSON.parse(saved) : []
  } catch {
    return []
  }
}

export const useChat = () => {
  const [messages, setMessages] = useState(loadMessages)
  const [sessionId, setSessionId] = useState(() => sessionStorage.getItem(SESSION_ID_KEY) || null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // Sync ke sessionStorage setiap kali messages berubah
  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(messages))
    } catch {
      // skip kalau sessionStorage penuh
    }
  }, [messages])

  const sendMessage = useCallback(async (query) => {
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString() 
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await sendChatMessage(query, sessionId)

      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id)
        sessionStorage.setItem(SESSION_ID_KEY, response.session_id)
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        hasSources: response.has_sources,
        timestamp: new Date().toISOString() 
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
    setSessionId(null)
    sessionStorage.removeItem(SESSION_KEY)
    sessionStorage.removeItem(SESSION_ID_KEY)
  }, [])

  return { messages, isLoading, error, sendMessage, clearMessages }
}