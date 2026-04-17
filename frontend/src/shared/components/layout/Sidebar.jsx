import { useAuth } from '@features/auth/context/AuthContext'
import { NavLink, useNavigate } from 'react-router-dom'

const NAV_ADMIN = [
  { to: '/dashboard',     label: 'Dashboard',      icon: <IconDashboard /> },
  { to: '/tickets',       label: 'Tickets',         icon: <IconTicket /> },
  { to: '/tickets/nuevo', label: 'Crear Ticket',    icon: <IconPlus /> },
  { to: '/agentes',       label: 'Agentes',         icon: <IconAgente /> },
  { to: '/clientes',      label: 'Clientes',        icon: <IconCliente /> },
  { to: '/areas',         label: 'Áreas',           icon: <IconArea /> },
  { to: '/instituciones', label: 'Instituciones',   icon: <IconInstitucion /> },
  { to: '/usuarios',      label: 'Usuarios',        icon: <IconUsuario /> },
]

const NAV_AGENTE = [
  { to: '/dashboard', label: 'Dashboard', icon: <IconDashboard /> },
  { to: '/tickets',   label: 'Tickets',   icon: <IconTicket /> },
]

const NAV_CLIENTE = [
  { to: '/dashboard',     label: 'Inicio',       icon: <IconDashboard /> },
  { to: '/tickets',       label: 'Mis Tickets',  icon: <IconTicket /> },
  { to: '/tickets/nuevo', label: 'Nuevo Ticket', icon: <IconPlus /> },
]

const NAV_MAP = {
  administrador: NAV_ADMIN,
  agente:        NAV_AGENTE,
  cliente:       NAV_CLIENTE,
}

export default function Sidebar() {
  const { user, rolActivo, logout } = useAuth()
  const navigate = useNavigate()
  const navItems = NAV_MAP[rolActivo] || []

  const iniciales = user
    ? `${user.nombres?.[0] || ''}${user.apellidos?.[0] || ''}`.toUpperCase()
    : '?'

  const ROL_LABELS = {
    administrador: 'Administrador',
    agente:        'Agente',
    cliente:       'Cliente',
  }

  return (
    <aside className="w-52 min-h-screen bg-gray-900 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-5 border-b border-gray-800">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5">
            <rect x="2" y="7" width="20" height="14" rx="2"/>
            <path d="M16 7V5a2 2 0 0 0-4 0v2"/>
          </svg>
        </div>
        <span className="text-white font-bold text-base">GeTICKET</span>
      </div>

      {/* Navegación */}
      <nav className="flex-1 px-3 py-4">
        <p className="text-gray-500 text-xs font-medium uppercase tracking-wider px-2 mb-3">
          Menú principal
        </p>
        <ul className="flex flex-col gap-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.to === '/dashboard'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                  ${isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`
                }
              >
                <span className="w-4 h-4 shrink-0">{item.icon}</span>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Usuario */}
      <div className="px-3 py-4 border-t border-gray-800">
        <div className="flex items-center gap-3 px-2 mb-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0">
            {iniciales}
          </div>
          <div className="overflow-hidden">
            <p className="text-white text-sm font-medium truncate">
              {user?.nombres} {user?.apellidos}
            </p>
            <p className="text-gray-400 text-xs truncate">
              {ROL_LABELS[rolActivo]}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/switch-rol')}
            className="flex-1 flex items-center justify-center gap-1.5 text-gray-400 hover:text-white text-xs py-1.5 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <polyline points="17 1 21 5 17 9"/>
              <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
              <polyline points="7 23 3 19 7 15"/>
              <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
            </svg>
            Cambiar rol
          </button>
          <button
            onClick={logout}
            className="flex-1 flex items-center justify-center gap-1.5 text-gray-400 hover:text-red-400 text-xs py-1.5 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Salir
          </button>
        </div>
      </div>
    </aside>
  )
}

// ── Iconos ──
function IconDashboard() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
}
function IconTicket() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/></svg>
}
function IconPlus() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
}
function IconAgente() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
}
function IconCliente() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
}
function IconArea() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
}
function IconInstitucion() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
}
function IconUsuario() {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
}