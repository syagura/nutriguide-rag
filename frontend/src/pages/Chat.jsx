import { useChat } from '../hooks/useChat'
import ChatBox from '../components/chat/ChatBox'
import './Chat.css'

const Chat = () => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat()

  return (
    <div className="chat-page">
      {/* Page header */}
      <div className="chat-header glass animate-fade-in">
        <div className="chat-header-left">
          <div className="chat-status-dot" />
          <div>
            <h1 className="chat-title">NutriGuide</h1>
            <p className="chat-subtitle">Pediatric nutrition assistant</p>
          </div>
        </div>
        {messages.length > 0 && (
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

      {/* Chat container */}
      <div className="chat-container glass animate-scale-in">
        <ChatBox
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSend={sendMessage}
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