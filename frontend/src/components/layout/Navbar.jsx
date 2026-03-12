import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Navbar.css'

const Navbar = () => {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/chat', label: 'Chat' },
    { path: '/about', label: 'About' }
  ]

  const handleLinkClick = () => setIsOpen(false)

  return (
    <>
      <nav className="navbar glass">
        <div className="navbar-inner">
          {/* Logo */}
          <Link to="/" className="navbar-logo" onClick={handleLinkClick}>
            <span className="logo-icon">N</span>
            <span className="logo-text">NutriGuide</span>
          </Link>

          {/* Desktop links */}
          <ul className="navbar-links desktop-only">
            {navLinks.map(link => (
              <li key={link.path}>
                <Link
                  to={link.path}
                  className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>

          {/* Desktop CTA */}
          <Link to="/chat" className="navbar-cta desktop-only">
            Try Now
          </Link>

          {/* Hamburger button — mobile only */}
          <button
            className="hamburger"
            onClick={() => setIsOpen(prev => !prev)}
            aria-label="Toggle menu"
          >
            {/* Animasi hamburger → X */}
            <span className={`bar ${isOpen ? 'open' : ''}`} />
            <span className={`bar ${isOpen ? 'open' : ''}`} />
            <span className={`bar ${isOpen ? 'open' : ''}`} />
          </button>
        </div>
      </nav>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div className="mobile-overlay animate-fade-in" onClick={() => setIsOpen(false)}>
          {/* Stop propagation supaya klik di dalam menu gak nutup overlay */}
          <div className="mobile-menu glass-heavy animate-scale-in" onClick={e => e.stopPropagation()}>
            <ul className="mobile-links">
              {navLinks.map(link => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className={`mobile-link ${location.pathname === link.path ? 'active' : ''}`}
                    onClick={handleLinkClick}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
            <Link to="/chat" className="btn-primary mobile-cta" onClick={handleLinkClick}>
              Try Now
            </Link>
          </div>
        </div>
      )}
    </>
  )
}

export default Navbar