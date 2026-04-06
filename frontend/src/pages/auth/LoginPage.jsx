import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { login, elegirRol } from '../../api/auth'

const ROL_CONFIG = {
  administrador: {
    label: 'Administrador',
    desc:  'Gestión completa del sistema',
    icon:  (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
  },
  agente: {
    label: 'Agente',
    desc:  'Atención y resolución de tickets',
    icon:  (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M3 18v-6a9 9 0 0 1 18 0v6"/>
        <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/>
        <path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>
      </svg>
    ),
  },
  cliente: {
    label: 'Cliente',
    desc:  'Crear y dar seguimiento a tickets',
    icon:  (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    ),
  },
}

export default function LoginPage() {
  const { guardarSesion } = useAuth()
  const navigate = useNavigate()

  const [tab, setTab]             = useState('login')
  const [form, setForm]           = useState({ username: '', password: '' })
  const [error, setError]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [pendiente, setPendiente] = useState(null)
  const [rolSelected, setRolSelected] = useState(null)

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await login(form)
      if (data.seleccionar_rol) {
        setPendiente(data)
        setRolSelected(data.roles[0])
      } else {
        guardarSesion(data)
        navigate('/dashboard')
      }
    } catch (err) {
      setError(
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.detail ||
        'Credenciales incorrectas.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleElegirRol = async () => {
    if (!rolSelected) return
    setLoading(true)
    try {
      const { data } = await elegirRol(pendiente.user_id, rolSelected)
      guardarSesion(data)
      navigate('/dashboard')
    } catch {
      setError('Error al seleccionar el rol.')
    } finally {
      setLoading(false)
    }
  }

  // ── Pantalla selección de rol ──
  if (pendiente) {
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
          Bienvenido, {pendiente.user.nombres}
        </h2>
        <p className="text-gray-500 text-sm mb-10">
          Selecciona el rol con el que deseas ingresar
        </p>

        <div className="flex gap-5 flex-wrap justify-center">
          {pendiente.roles.map((rol) => {
            const cfg    = ROL_CONFIG[rol]
            const activo = rolSelected === rol
            return (
              <button
                key={rol}
                onClick={() => handleElegirRol(rol)}
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

        <button
          onClick={() => setPendiente(null)}
          className="mt-8 text-sm text-gray-400 hover:text-gray-600 transition-colors"
        >
          ← Volver al login
        </button>
      </div>
    )
  }

  // ── Pantalla login / registro ──
  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-blue-900 to-blue-700 flex-col items-center justify-center p-12 text-white">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-14 h-14 bg-blue-500 rounded-2xl flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="white" className="w-8 h-8">
              <rect x="2" y="7" width="20" height="14" rx="2"/>
              <path d="M16 7V5a2 2 0 0 0-4 0v2"/>
            </svg>
          </div>
          <span className="text-3xl font-bold">GeTICKET</span>
        </div>
        <p className="text-blue-200 text-center text-lg max-w-xs leading-relaxed">
          Sistema Web Help Desk corporativo. Gestión eficiente de tickets, equipos y áreas.
        </p>
      </div>

      {/* Panel derecho */}
      <div className="flex-1 bg-gray-50 flex items-center justify-center p-8">
        <div className="w-full max-w-md">

          {/* Tabs */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-8">
            <button
              onClick={() => setTab('login')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all
                ${tab === 'login' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                <polyline points="10 17 15 12 10 7"/>
                <line x1="15" y1="12" x2="3" y2="12"/>
              </svg>
              Iniciar sesión
            </button>
            <button
              onClick={() => setTab('registro')}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all
                ${tab === 'registro' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <line x1="19" y1="8" x2="19" y2="14"/>
                <line x1="22" y1="11" x2="16" y2="11"/>
              </svg>
              Registrarse
            </button>
          </div>

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Usuario
                </label>
                <input
                  name="username"
                  type="text"
                  value={form.username}
                  onChange={handleChange}
                  required
                  placeholder="Ingrese su usuario"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Contraseña
                </label>
                <input
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={handleChange}
                  required
                  placeholder="Ingrese su contraseña"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
              </div>
              {error && <p className="text-red-500 text-sm">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 rounded-xl transition-colors mt-1"
              >
                {loading ? 'Ingresando...' : 'Iniciar sesión'}
              </button>
            </form>
          ) : (
            <RegisterForm />
          )}
        </div>
      </div>
    </div>
  )
}

function RegisterForm() {
  const [form, setForm] = useState({
    nombres: '', apellidos: '', ci: '', nro_celular: '',
    email: '', user_telegram: '', id_institucion: '', rol_institucion: '',
    username: '', password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [success, setSuccess] = useState(false)

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      // Endpoint de registro público — lo implementamos después
      setSuccess(true)
    } catch (err) {
      setError('Error al crear la cuenta.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-8 h-8 text-green-600">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">¡Cuenta creada!</h3>
        <p className="text-gray-500 text-sm">Un administrador activará tu cuenta pronto.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Nombres</label>
          <input name="nombres" value={form.nombres} onChange={handleChange} required
            placeholder="Nombres"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Apellidos</label>
          <input name="apellidos" value={form.apellidos} onChange={handleChange} required
            placeholder="Apellidos"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">CI</label>
          <input name="ci" value={form.ci} onChange={handleChange}
            placeholder="Cédula de identidad"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Nro. de celular</label>
          <input name="nro_celular" value={form.nro_celular} onChange={handleChange}
            placeholder="+591 ..."
            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Correo electrónico</label>
        <input name="email" type="email" value={form.email} onChange={handleChange} required
          placeholder="correo@ejemplo.com"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Usuario de Telegram (opcional)</label>
        <input name="user_telegram" value={form.user_telegram} onChange={handleChange}
          placeholder="@usuario"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Usuario</label>
        <input name="username" value={form.username} onChange={handleChange} required
          placeholder="nombre_usuario"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">Contraseña</label>
        <input name="password" type="password" value={form.password} onChange={handleChange} required
          placeholder="••••••••"
          className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"/>
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 rounded-xl transition-colors mt-1">
        {loading ? 'Creando cuenta...' : 'Crear cuenta'}
      </button>
    </form>
  )
}