import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { login, elegirRol } from '../../api/auth'

export default function LoginPage() {
  const { guardarSesion } = useAuth()
  const navigate = useNavigate()

  const [form, setForm]           = useState({ username: '', password: '' })
  const [error, setError]         = useState('')
  const [loading, setLoading]     = useState(false)

  // Estado para selección de rol
  const [pendiente, setPendiente] = useState(null) // { user_id, roles, user }

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await login(form)
      if (data.seleccionar_rol) {
        // Tiene múltiples roles — mostrar selección
        setPendiente(data)
      } else {
        // Un solo rol — entrar directo
        guardarSesion(data)
        navigate('/dashboard')
      }
    } catch (err) {
      setError(
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        'Error al iniciar sesión.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleElegirRol = async (rol) => {
    setError('')
    setLoading(true)
    try {
      const { data } = await elegirRol(pendiente.user_id, rol)
      guardarSesion(data)
      navigate('/dashboard')
    } catch (err) {
      setError('Error al seleccionar el rol.')
    } finally {
      setLoading(false)
    }
  }

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

  // Vista de selección de rol
  if (pendiente) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-md p-8">
          <div className="text-center mb-8">
            <p className="text-gray-500 text-sm mb-1">Bienvenido</p>
            <h2 className="text-xl font-semibold text-gray-900">
              {pendiente.user.nombres} {pendiente.user.apellidos}
            </h2>
            <p className="text-gray-500 text-sm mt-4">
              Tienes múltiples roles. ¿Con cuál quieres ingresar?
            </p>
          </div>

          <div className="flex flex-col gap-3">
            {pendiente.roles.map((rol) => (
              <button
                key={rol}
                onClick={() => handleElegirRol(rol)}
                disabled={loading}
                className={`w-full py-4 px-6 rounded-xl border-2 text-left font-medium transition-all ${ROL_COLORS[rol]}`}
              >
                {ROL_LABELS[rol]}
              </button>
            ))}
          </div>

          {error && (
            <p className="text-red-500 text-sm text-center mt-4">{error}</p>
          )}

          <button
            onClick={() => setPendiente(null)}
            className="w-full mt-4 text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Volver
          </button>
        </div>
      </div>
    )
  }

  // Vista de login
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-md p-8">

        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">GeTiket</h1>
          <p className="text-gray-500 text-sm mt-1">Sistema de soporte</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Usuario
            </label>
            <input
              name="username"
              type="text"
              value={form.username}
              onChange={handleChange}
              required
              placeholder="tu_usuario"
              className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña
            </label>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-xl border border-gray-300 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2.5 rounded-xl transition-colors mt-2"
          >
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
      </div>
    </div>
  )
}