// API base URL — switch antara dev dan production
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// App info
export const APP_NAME = 'NutriGuide'
export const APP_TAGLINE = 'Evidence-based pediatric nutrition guidance, powered by AI'
export const APP_VERSION = '1.0.0'

// Chat config
export const MAX_QUERY_LENGTH = 500
export const MIN_QUERY_LENGTH = 3

// Typing animation speed (ms per character)
export const TYPING_SPEED = 12