import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../../context/AuthContext'
import { elegirRol, switchRol } from '../../../api/auth'

const ROL_CONFIG = {
  administrador: {
    label: 'Administrador',
    desc: 'Gestión completa del sistema',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
  },
  agente: {
    label: 'Agente',
    desc: 'Atención y resolución de tickets',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M3 18v-6a9 9 0 0 1 18 0v6"/>
        <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/>
        <path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>
      </svg>
    ),
  },
  cliente: {
    label: 'Cliente',
    desc: 'Crear y dar seguimiento a tickets',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    ),
  },
}

export default function RoleSelector({ 
  mode = 'initial', // 'initial' (después de login) o 'switch' (cambio desde menú)
  userData = null,  // para modo 'initial' (contiene user_id, user, roles)
  onCancel = null,  // función para volver atrás (solo en modo 'initial')
}) {
  const { guardarSesion, actualizarRol, roles: contextRoles, user } = useAuth()
  const navigate = useNavigate()
  const [selectedRole, setSelectedRole] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Determinar lista de roles según el modo
  const availableRoles = mode === 'initial' 
    ? userData?.roles || []
    : contextRoles || []

  const displayName = mode === 'initial'
    ? userData?.user?.nombres || 'Usuario'
    : user?.nombres || 'Usuario'

  const handleSelectRole = (rol) => {
    setSelectedRole(rol)
  }

  const handleConfirm = async () => {
    if (!selectedRole) return
    setLoading(true)
    setError('')
    
    try {
      if (mode === 'initial') {
        // Login inicial: usar elegirRol
        const { data } = await elegirRol(userData.user_id, selectedRole)
        guardarSesion(data)
        navigate('/dashboard')
      } else {
        // Cambio de rol desde menú: usar switchRol
        const { data } = await switchRol(selectedRole)
        actualizarRol(data)
        navigate('/dashboard')
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error al seleccionar el rol. Intente nuevamente.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      {/* Logo */}
      <div className="flex items-center gap-2 mb-10">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
            <rect x="2" y="7" width="20" height="14" rx="2"/>
            <path d="M16 7V5a2 2 0 0 0-4 0v2"/>
          </svg>
        </div>
        <span className="text-xl font-bold text-gray-900">GeTICKET</span>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-1">
        {mode === 'initial' ? `Bienvenido, ${displayName}` : 'Cambiar rol'}
      </h2>
      <p className="text-gray-500 text-sm mb-10">
        {mode === 'initial' 
          ? 'Selecciona el rol con el que deseas ingresar'
          : 'Selecciona el rol al que deseas cambiar'
        }
      </p>

      <div className="flex gap-5 flex-wrap justify-center">
        {availableRoles.map((rol) => {
          const cfg = ROL_CONFIG[rol]
          const activo = selectedRole === rol
          return (
            <button
              key={rol}
              onClick={() => handleSelectRole(rol)}
              disabled={loading}
              className={`w-52 p-8 rounded-2xl border-2 flex flex-col items-center gap-4 transition-all bg-white
                ${activo
                  ? 'border-blue-500 shadow-lg scale-105'
                  : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                }`}
            >
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors
                ${activo ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'}`}>
                <span className="w-8 h-8">{cfg.icon}</span>
              </div>
              <div className="text-center">
                <p className="font-semibold text-gray-900 text-base">{cfg.label}</p>
                <p className="text-gray-500 text-xs mt-1 leading-relaxed">{cfg.desc}</p>
              </div>
            </button>
          )
        })}
      </div>

      {error && <p className="text-red-500 text-sm mt-6">{error}</p>}

      <div className="flex gap-4 mt-8">
        <button
          onClick={handleConfirm}
          disabled={!selectedRole || loading}
          className={`px-8 py-3 rounded-xl font-medium transition-colors ${
            selectedRole && !loading
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {loading ? 'Procesando...' : 'Confirmar'}
        </button>
        
        {mode === 'initial' && onCancel && (
          <button
            onClick={onCancel}
            className="px-8 py-3 rounded-xl font-medium text-gray-500 hover:text-gray-700 transition-colors"
          >
            ← Volver al login
          </button>
        )}
        {mode === 'switch' && (
          <button
            onClick={() => navigate('/dashboard')}
            className="px-8 py-3 rounded-xl font-medium text-gray-500 hover:text-gray-700 transition-colors"
          >
            Cancelar
          </button>
        )}
      </div>
    </div>
  )
}