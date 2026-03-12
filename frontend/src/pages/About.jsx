import { Link } from 'react-router-dom'
import './About.css'

const stack = [
    { category: 'Backend', items: ['FastAPI', 'Python 3.10', 'Pydantic'] },
    { category: 'RAG Pipeline', items: ['FAISS', 'BM25Okapi', 'RRF Fusion', 'Cross-Encoder Reranker'] },
    { category: 'LLM & Embeddings', items: ['Groq (Llama 3.1 8B)', 'Multilingual MiniLM', 'SentenceTransformers'] },
    { category: 'Evaluation', items: ['RAGAS', 'Faithfulness', 'Answer Relevancy', 'Context Precision'] },
    { category: 'Frontend', items: ['React', 'Vite', 'Tailwind CSS v4'] },
    { category: 'Knowledge Bases', items: ['WHO Child Growth Standards', 'Kemenkes RI', 'UNICEF Guidelines', 'Buku KIA'] }
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
            from PDF ingestion to evaluated LLM responses.
            </p>
        </div>

        {/* Architecture diagram (text-based) */}
        <div className="arch-section animate-fade-in-up stagger-2">
            <h2 className="section-label">Architecture</h2>
            <div className="arch-flow glass">
            {[
                { icon: '📄', label: 'PDF Ingestion', sub: 'PyMuPDF' },
                { icon: '✂️', label: 'Chunking', sub: 'LangChain 512 tokens' },
                { icon: '🔢', label: 'Embedding', sub: 'Multilingual MiniLM' },
                { icon: '🔍', label: 'Hybrid Search', sub: 'FAISS + BM25 + RRF' },
                { icon: '🎯', label: 'Reranking', sub: 'Cross-Encoder' },
                { icon: '🤖', label: 'Generation', sub: 'Llama 3.1 via Groq' }
            ].map((step, i, arr) => (
                <div key={i} className="arch-step-wrap">
                <div className="arch-step">
                    <span className="arch-icon">{step.icon}</span>
                    <span className="arch-step-label">{step.label}</span>
                    <span className="arch-step-sub">{step.sub}</span>
                </div>
                {i < arr.length - 1 && (
                    <span className="arch-arrow">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <line x1="5" y1="12" x2="19" y2="12" />
                        <polyline points="12 5 19 12 12 19" />
                    </svg>
                    </span>
                )}
                </div>
            ))}
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