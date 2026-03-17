import { Link } from 'react-router-dom'
import './About.css'

const stack = [
  { category: 'Backend', items: ['FastAPI', 'Python 3.10', 'Pydantic'] },
  { category: 'RAG Pipeline', items: ['FAISS', 'BM25Okapi', 'RRF Fusion', 'Cross-Encoder Reranker'] },
  { category: 'LLM & Embeddings', items: ['Groq (Llama 3.1 8B)', 'Multilingual MiniLM', 'SentenceTransformers'] },
  { category: 'Evaluation', items: ['RAGAS', 'Faithfulness', 'Answer Relevancy', 'Context Precision'] },
  { category: 'Frontend', items: ['React', 'Vite', 'Tailwind CSS v4'] },
  { category: 'Knowledge Bases', items: ['WHO - World Health Organization', 'UNICEF - Child Nutrition Division', 'KEMENKES RI - Ministry of Health', 'Buku KIA - Maternal & Child Health'] }
]

const About = () => {
  return (
    <div className="about-page">
      {/* Header */}
      <div className="about-header animate-fade-in-up stagger-1">
        <p className="about-eyebrow">Portfolio Project</p>
        <h1 className="about-title">How NutriGuide works</h1>
        <p className="about-desc">
          An end-to-end RAG system built to demonstrate production-grade AI engineering —
          from PDF ingestion to evaluated LLM responses. Powered by 22 official documents
          from WHO, UNICEF, KEMENKES RI, and Buku KIA.
        </p>
      </div>

      {/* Architecture diagram (text-based) */}
      <div className="arch-section animate-fade-in-up stagger-2">
        <h2 className="section-label">Architecture</h2>
        <div className='arch-diagram-wrap'>
          <img 
            src="/architecture.png" 
            alt="NutriGuide RAG Architecture Diagram" 
            className='arch-diagram-img'
          />
        </div>
      </div>

      {/* Tech stack */}
      <div className="stack-section animate-fade-in-up stagger-3">
        <h2 className="section-label">Tech Stack</h2>
        <div className="stack-grid">
          {stack.map((group, i) => (
            <div key={i} className="stack-card glass">
              <p className="stack-category">{group.category}</p>
              <ul className="stack-items">
                {group.items.map((item, j) => (
                  <li key={j} className="stack-item">
                    <span className="stack-dot" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Design decisions */}
      <div className="decisions-section animate-fade-in-up stagger-4">
        <h2 className="section-label">Key Design Decisions</h2>
        <div className="decisions-list">
          {[
            {
              title: 'Why Groq instead of local LLM?',
              desc: 'Limited RAM (8GB) makes running Phi-3 Mini uncomfortable locally. Groq provides free-tier Llama 3.1 8B with LPU inference — significantly faster and higher quality.'
            },
            {
              title: 'Why Hybrid Retrieval?',
              desc: 'Pure semantic search misses exact keywords like "stunting usia 6 bulan". BM25 captures exact matches while FAISS captures semantic meaning. RRF combines both without additional training.'
            },
            {
              title: 'Why Multilingual Embeddings?',
              desc: 'Knowledge base is mixed Indonesian (Kemenkes, KIA) and English (WHO, UNICEF). Monolingual English models drop quality on Indonesian text significantly.'
            },
            {
              title: 'Why Cross-Encoder Reranking?',
              desc: 'Bi-encoders embed query and document independently. Cross-encoders read them together, capturing fine-grained relevance interactions — critical for medical accuracy.'
            }
          ].map((d, i) => (
            <div key={i} className="decision-item glass">
              <h3 className="decision-title">{d.title}</h3>
              <p className="decision-desc">{d.desc}</p>
            </div>
          ))}
        </div>
      </div>
      
      {/* Built by */}
      <div className="built-by-section animate-fade-in-up stagger-5">
        <h2 className="section-label">Built by</h2>
        <div className="builder-card glass">
          <div className="builder-left">
            <div className="builder-avatar">
              {/* Ganti src dengan foto lo bre kalau mau pake foto */}
              <img src="/me.JPG" alt="Syahrul" className="builder-photo" />
              {/* <span className="builder-initial">S</span> */}
            </div>
            <div className="builder-info">
              <h3 className="builder-name">Syahrul Gunawan Ramdhani</h3>
              <p className="builder-role">AI/ML Engineer · Data Scientist</p>
              <p className="builder-desc">
                Bangkit Academy 2024 graduate specializing in end-to-end ML systems —
                from RAG pipelines and NLP to computer vision and edge deployment.
                Building production-ready AI solutions that solve real-world problems.
              </p>
              <div className="builder-tags">
                <span className="builder-tag">RAG</span>
                <span className="builder-tag">NLP</span>
                <span className="builder-tag">Computer Vision</span>
                <span className="builder-tag">FastAPI</span>
                <span className="builder-tag">TensorFlow</span>
              </div>
            </div>
          </div>
          <div className="builder-links">
            <a
              href="https://linkedin.com/in/syahrulgunawanramdhani"
              target="_blank"
              rel="noopener noreferrer"
              className="builder-link"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                <rect x="2" y="9" width="4" height="12"/>
                <circle cx="4" cy="4" r="2"/>
              </svg>
              LinkedIn
            </a>
            <a
              href="https://github.com/syagura"
              target="_blank"
              rel="noopener noreferrer"
              className="builder-link"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
              GitHub
            </a>
            <a
              href="mailto:syahrulgunawanramdhani@gmail.com"
              className="builder-link"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,12 2,6"/>
              </svg>
              Email
            </a>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="about-cta animate-fade-in-up stagger-5">
        <Link to="/chat" className="btn-primary">Try NutriGuide</Link>
        <a
          href="https://github.com/syagura/nutriguide-rag"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-secondary"
        >
          View on GitHub
        </a>
      </div>
    </div>
  )
}

export default About