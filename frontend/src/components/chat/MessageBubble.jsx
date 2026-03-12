import { useEffect, useState } from 'react'
import CitationCard from './CitationCard'
import LoadingDots from '../ui/LoadingDots'
import { TYPING_SPEED } from '../../constants'
import './MessageBubble.css'

const MessageBubble = ({ message, isLatest }) => {
  const isUser = message.role === 'user'
  const isLoading = message.role === 'loading'

  // State untuk typing animation — karakter muncul satu per satu
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  useEffect(() => {
    // Typing animation hanya untuk pesan assistant terbaru
    // pesan lama langsung muncul sekaligus tanpa animasi
    if (!isUser && !isLoading && isLatest && message.content) {
      setIsTyping(true)
      setDisplayedText('')

      let i = 0
      const interval = setInterval(() => {
        if (i < message.content.length) {
          // Tambah karakter satu per satu
          setDisplayedText(message.content.slice(0, i + 1))
          i++
        } else {
          clearInterval(interval)
          setIsTyping(false)
        }
      }, TYPING_SPEED)

      // Cleanup interval kalau component unmount sebelum selesai
      return () => clearInterval(interval)
    } else if (!isUser && !isLoading) {
      // Pesan lama langsung tampil penuh
      setDisplayedText(message.content)
    }
  }, [message.content, isUser, isLoading, isLatest])

  if (isLoading) {
    return (
      <div className="message-row assistant animate-fade-in">
        <div className="message-avatar assistant-avatar">N</div>
        <div className="message-bubble assistant-bubble loading-bubble">
          <LoadingDots />
        </div>
      </div>
    )
  }

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'} animate-fade-in-up`}>
      {!isUser && (
        <div className="message-avatar assistant-avatar">N</div>
      )}

      <div className={`message-content-wrap ${isUser ? 'user-wrap' : ''}`}>
        <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
          <p className="message-text">
            {isUser ? message.content : displayedText}
            {/* Blinking cursor saat masih ngetik */}
            {isTyping && <span className="typing-cursor" />}
          </p>
        </div>

        {/* Citation card muncul setelah typing selesai */}
        {!isUser && !isTyping && message.hasSources && (
          <CitationCard sources={message.sources} />
        )}
      </div>

      {isUser && (
        <div className="message-avatar user-avatar">U</div>
      )}
    </div>
  )
}

export default MessageBubble