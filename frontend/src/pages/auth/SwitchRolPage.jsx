import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { switchRol } from '../../api/auth'
import { useState } from 'react'

export default function SwitchRolPage() {
  const { user, roles, rolActivo, actualizarRol } = useAuth()
  const navigate  = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const ROL_LABELS = {
    administrador: 'Administrador',
    agente:        'Agente',
    cliente:       'Cliente',
  }

  const ROL_COLORS = {
    administrador: 'bg-purple-100 text-purple-800 border-purple-300 hover:bg-purple-200',
    agente:        'bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200',
    cliente:       'bg-green-100 text-green-800 border-green-300 hover:bg-green-200',
  }

  const handleSwitch = async (rol) => {
    if (rol === rolActivo) return
    setLoading(true)
    setError('')
    try {
      const { data } = await switchRol(rol)
      actualizarRol(data)
      navigate('/dashboard')
    } catch {
      setError('Error al cambiar de rol.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h2 className="text-xl font-semibold text-gray-900">Cambiar rol</h2>
          <p className="text-gray-500 text-sm mt-1">
            Actualmente eres <span className="font-medium">{ROL_LABELS[rolActivo]}</span>
          </p>
        </div>

        <div className="flex flex-col gap-3">
          {roles.map((rol) => (
            <button
              key={rol}
              onClick={() => handleSwitch(rol)}
              disabled={loading || rol === rolActivo}
              className={`w-full py-4 px-6 rounded-xl border-2 text-left font-medium transition-all
                ${rol === rolActivo
                  ? 'opacity-40 cursor-not-allowed border-gray-200 bg-gray-50 text-gray-500'
                  : ROL_COLORS[rol]
                }`}
            >
              {ROL_LABELS[rol]}
              {rol === rolActivo && (
                <span className="text-xs ml-2">(actual)</span>
              )}
            </button>
          ))}
        </div>

        {error && (
          <p className="text-red-500 text-sm text-center mt-4">{error}</p>
        )}

        <button
          onClick={() => navigate(-1)}
          className="w-full mt-4 text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          Volver
        </button>
      </div>
    </div>
  )
}