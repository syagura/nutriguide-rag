import { useState, useEffect } from 'react'
import { waitForBackend } from '../utils/api'
import { useChat } from '../hooks/useChat'
import ChatBox from '../components/chat/ChatBox'
import './Chat.css'

const STATUS_TEXT = {
  checking: 'Checking system status...',
  warming_up: 'Warming up the server, please wait...',
  ready: null,
  failed: 'Server unavailable, Please try again later.'
}

const Chat = () => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat()
  const [backendStatus, setBackendStatus] = useState('checking')

  useEffect(() => {
    waitForBackend(setBackendStatus)
  }, [])

  return (
    <div className="chat-page">
      {/* Page header */}
      <div className="chat-header glass animate-fade-in">
        <div className="chat-header-left">
          <div className={`chat-status-dot ${backendStatus !== 'ready' ? 'warming' : ''}`} />
          <div>
            <h1 className="chat-title">NutriGuide</h1>
            <p className="chat-subtitle">
              {backendStatus === 'ready'
                ? 'Pediatric nutrition assistant'
                : STATUS_TEXT[backendStatus]
              }
              </p>
          </div>
        </div>
        {messages.length > 0 && backendStatus === 'ready' && (
          <button className="clear-btn" onClick={clearMessages}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
              <path d="M10 11v6M14 11v6" />
            </svg>
            Clear chat
          </button>
        )}
      </div>

      {/* Waming up banner  */}
      {backendStatus !== 'ready' && backendStatus !== 'failed' && (
        <div className='warming-banner glass animate-fade-in'>
          <div className='warming-spinner' />
          <p className='warming-text'>
            Server is waking up - this may take up to 30 seconds on first load.
          </p>
        </div>
      )}

      {/* failed banner */}
      {backendStatus === 'failed' && (
        <div className='failed-banner animate-fade-in'>
          <p>Could not connect to server. Please refresh the page.</p>
        </div>
      )}

      {/* Chat container */}
      <div className={`chat-container glass animate-scale-in ${backendStatus !== 'ready' ? 'chat-disable' : ''}`}>
        <ChatBox
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSend={backendStatus === 'ready' ? sendMessage : undefined}
          disabled={backendStatus !== 'ready'}
        />
      </div>

      {/* Disclaimer */}
      <p className="chat-disclaimer animate-fade-in">
        NutriGuide provides information based on official medical documents.
        Always consult a healthcare professional for medical advice.
      </p>
    </div>
  )
}

export default Chat