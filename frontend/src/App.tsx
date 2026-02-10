import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import OpportunityTable from './components/OpportunityTable'
import LoginPrompt from './components/LoginPrompt'
import { authApi } from './services/api'

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    authApi
      .status()
      .then((res) => setAuthenticated(res.data.authenticated))
      .catch(() => setAuthenticated(false))
  }, [])

  if (authenticated === null) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!authenticated) {
    return <LoginPrompt />
  }

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/opportunities" element={<OpportunityTable />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
