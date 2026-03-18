import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/layout/Navbar'
import Landing from './pages/Landing'
import Chat from './pages/Chat'
import About from './pages/About'
import { startKeepAlive } from './utils/api'

const App = () => {
  useEffect(() => {
    const interval = startKeepAlive()
    return () => clearInterval(interval)
  }, [])
  
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App