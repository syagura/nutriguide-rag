import { useState } from 'react'
import './CitationCard.css'

const CitationCard = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="citation-wrapper">
      {/* Toggle button buat show/hide sources */}
      <button
        className="citation-toggle"
        onClick={() => setIsOpen(prev => !prev)}
      >
        <span className="citation-icon">
          {/* Stack icon buat sumber dokumen */}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
        </span>
        <span>{sources.length} source{sources.length > 1 ? 's' : ''}</span>
        {/* Chevron yang rotate saat open */}
        <span className={`citation-chevron ${isOpen ? 'open' : ''}`}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </span>
      </button>

      {/* Dropdown sources — glossy glass style */}
      {isOpen && (
        <div className="citation-dropdown animate-scale-in">
          <p className="citation-label">Referenced documents</p>
          <ul className="citation-list">
            {sources.map((source, idx) => (
              <li key={idx} className="citation-item">
                <span className="citation-num">{idx + 1}</span>
                <span className="citation-source">{source}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default CitationCard