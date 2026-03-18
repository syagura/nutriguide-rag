import { useRef, useEffect, useState } from 'react'
import MessageBubble from './MessageBubble'
import { MAX_QUERY_LENGTH, MIN_QUERY_LENGTH } from '../../constants'
import './ChatBox.css'

const ChatBox = ({ messages, isLoading, error, onSend, disabled = false }) => {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll ke bawah setiap ada pesan baru
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Auto-resize textarea sesuai konten
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`
    }
  }, [input])

  const handleSend = () => {
    const trimmed = input.trim()
    if (trimmed.length < MIN_QUERY_LENGTH || isLoading || disabled) return
    onSend(trimmed)
    setInput('')
  }

  const handleKeyDown = (e) => {
    // Enter tanpa Shift = send, Shift+Enter = newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isValid = input.trim().length >= MIN_QUERY_LENGTH
  const charsLeft = MAX_QUERY_LENGTH - input.length

  return (
    <div className="chatbox-container">
      {/* Messages area */}
      <div className="messages-area">
        {messages.length === 0 && (
          <div className="empty-state animate-fade-in">
            <div className="empty-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z" />
                <path d="M12 8v4l3 3" />
              </svg>
            </div>
            <h3 className="empty-title">Ask NutriGuide</h3>
            <p className="empty-subtitle">
              Get evidence-based answers about pediatric nutrition from WHO, Kemenkes RI, UNICEF, and Buku KIA.
            </p>
            {/* Suggested questions */}
            <div className="suggestions">
              {[
                "What are iron requirements for a 6-month-old?",
                "How to prevent stunting in toddlers?",
                "When should I start MPASI?"
              ].map((suggestion, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => !disabled && onSend(suggestion)}
                  disabled={disabled}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            isLatest={idx === messages.length - 1}
          />
        ))}

        {/* Loading bubble saat nunggu response */}
        {isLoading && (
          <MessageBubble
            message={{ role: 'loading' }}
            isLatest={true}
          />
        )}

        {/* Error message */}
        {error && (
          <div className="error-banner animate-fade-in">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="input-area glass">
        <div className="input-wrap">
          <textarea
            ref={textareaRef}
            className="chat-input"
            placeholder={disabled ? "Waiting for server..." : "Ask about pediatric nutrition..."}
            value={input}
            onChange={e => setInput(e.target.value.slice(0, MAX_QUERY_LENGTH))}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading || disabled}
          />
          <div className="input-footer">
            {/* Char counter — muncul kalau udah dekat limit */}
            {input.length > MAX_QUERY_LENGTH * 0.8 && (
              <span className={`char-count ${charsLeft < 50 ? 'warning' : ''}`}>
                {charsLeft}
              </span>
            )}
            <span className="input-hint">Shift+Enter for new line</span>
            <button
              className={`send-btn ${isValid && !isLoading && !disabled ? 'active' : ''}`}
              onClick={handleSend}
              disabled={!isValid || isLoading || disabled}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatBox