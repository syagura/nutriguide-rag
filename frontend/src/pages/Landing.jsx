import { Link } from 'react-router-dom'
import './Landing.css'

const features = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      </svg>
    ),
    title: 'Evidence-Based',
    desc: 'Answers grounded in WHO, Kemenkes RI, UNICEF, and Buku KIA — not hallucinations.'
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
    title: 'Hybrid Retrieval',
    desc: 'Semantic + keyword search with Reciprocal Rank Fusion for precise context retrieval.'
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    title: 'RAGAS Evaluated',
    desc: 'Faithfulness, relevancy, and precision metrics ensure reliable, trustworthy answers.'
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
        <line x1="8" y1="21" x2="16" y2="21" />
        <line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
    title: 'Source Citations',
    desc: 'Every answer links back to its source document and page — full transparency.'
  }
]

const steps = [
  { num: '01', title: 'Ask a question', desc: 'Type any question about child nutrition, growth, or feeding.' },
  { num: '02', title: 'RAG retrieves context', desc: 'Hybrid retrieval finds the most relevant passages from medical documents.' },
  { num: '03', title: 'LLM generates answer', desc: 'GPT-OSS-20B generates a grounded, evidence-based response.' },
  { num: '04', title: 'View sources', desc: 'Expand citations to see exactly which documents were referenced.' }
]

const Landing = () => {
  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        {/* Background mesh gradient */}
        <div className="hero-bg">
          <div className="mesh-1" />
          <div className="mesh-2" />
        </div>

        <div className="hero-content">
          <div className="hero-badge animate-fade-in-up stagger-1">
            <span className="badge-dot" />
            RAG-Powered · Evidence-Based · Open Source
          </div>

          <h1 className="hero-title animate-fade-in-up stagger-2">
            Pediatric Nutrition<br />
            <span className="title-accent">Guidance You Can Trust</span>
          </h1>

          <p className="hero-subtitle animate-fade-in-up stagger-3">
            NutriGuide combines retrieval-augmented generation with official medical
            knowledge bases to deliver accurate, cited answers about child nutrition.
          </p>

          <div className="hero-actions animate-fade-in-up stagger-4">
            <Link to="/chat" className="btn-primary">
              Start Asking
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </Link>
            <Link to="/about" className="btn-secondary">
              How it works
            </Link>
          </div>

          {/* Floating stats */}
          <div className="hero-stats animate-fade-in-up stagger-5">
            {[
              { val: '22', label: 'Knowledge Documents' },
              { val: 'RAG', label: 'Architecture' },
              { val: 'LLM', label: 'OPENAI/GPT-OSS-80B' }
            ].map((stat, i) => (
              <div key={i} className="stat-item glass">
                <span className="stat-val">{stat.val}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="section-header">
          <p className="section-eyebrow">Why NutriGuide</p>
          <h2 className="section-title">Built for accuracy, not convenience</h2>
        </div>
        <div className="features-grid">
          {features.map((f, i) => (
            <div key={i} className={`feature-card glass animate-fade-in-up stagger-${i + 1}`}>
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="steps-section">
        <div className="section-header">
          <p className="section-eyebrow">The Pipeline</p>
          <h2 className="section-title">From question to cited answer</h2>
        </div>
        <div className="steps-list">
          {steps.map((step, i) => (
            <div key={i} className={`step-item animate-fade-in-up stagger-${i + 1}`}>
              <div className="step-num">{step.num}</div>
              <div className="step-content">
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.desc}</p>
              </div>
              {i < steps.length - 1 && <div className="step-connector" />}
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-card glass-heavy">
          <div className="cta-glow" />
          <h2 className="cta-title">Ready to ask?</h2>
          <p className="cta-desc">Get evidence-based answers about pediatric nutrition in seconds.</p>
          <Link to="/chat" className="btn-primary">
            Open Chat
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>Built with FastAPI · FAISS · LangChain · Groq · React</p>
        <p className="footer-sub">NutriGuide · AI/ML Engineer Portfolio Project</p>
      </footer>
    </div>
  )
}

export default Landing