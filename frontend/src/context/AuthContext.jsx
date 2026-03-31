import { createContext, useContext, useState, useEffect } from 'react'
import { getMe } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]           = useState(null)
  const [rolActivo, setRolActivo] = useState(null)
  const [roles, setRoles]         = useState([])
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      getMe()
        .then(({ data }) => {
          setUser(data)
          setRolActivo(data.rol_activo)
          setRoles(data.roles)
        })
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const guardarSesion = (data) => {
    localStorage.setItem('access_token',  data.access)
    localStorage.setItem('refresh_token', data.refresh)
    setUser(data.user)
    setRolActivo(data.rol_activo)
    setRoles(data.roles)
  }

  const actualizarRol = (data) => {
    localStorage.setItem('access_token',  data.access)
    localStorage.setItem('refresh_token', data.refresh)
    setRolActivo(data.rol_activo)
    setRoles(data.roles)
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
    setRolActivo(null)
    setRoles([])
  }

  return (
    <AuthContext.Provider value={{
      user, rolActivo, roles, loading,
      guardarSesion, actualizarRol, logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)