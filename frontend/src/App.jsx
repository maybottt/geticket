import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './routes/PrivateRoute'
import LoginPage from './pages/auth/LoginPage'
import SwitchRolPage from './pages/auth/SwitchRolPage'

// Placeholder temporal para dashboard
function Dashboard() {
  const { useAuth } = require('./context/AuthContext')
  return null
}

function DashboardTemp() {
  const { user, rolActivo, logout } = window.__auth || {}
  return (
    <div className="p-8">
      <p className="text-gray-600">Dashboard — próximamente</p>
    </div>
  )
}

import { useAuth } from './context/AuthContext'

function DashboardPage() {
  const { user, rolActivo, logout } = useAuth()
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-xl mx-auto bg-white rounded-2xl border border-gray-200 p-8">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">
          Hola, {user?.nombres} 👋
        </h1>
        <p className="text-gray-500 text-sm mb-6">
          Rol activo: <span className="font-medium capitalize">{rolActivo}</span>
        </p>
        <div className="flex gap-3">
          
           <a href="/switch-rol"
            className="px-4 py-2 rounded-lg bg-blue-50 text-blue-700 text-sm font-medium hover:bg-blue-100 transition"
          >
            Cambiar rol
          </a>
          <button
            onClick={logout}
            className="px-4 py-2 rounded-lg bg-red-50 text-red-600 text-sm font-medium hover:bg-red-100 transition"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/switch-rol" element={
            <PrivateRoute><SwitchRolPage /></PrivateRoute>
          } />
          <Route path="/dashboard" element={
            <PrivateRoute><DashboardPage /></PrivateRoute>
          } />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}