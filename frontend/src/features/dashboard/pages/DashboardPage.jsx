import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDashboardStats } from "@features/tickets/api/tickets";
import AppLayout from "@shared/components/layout/AppLayout"; 

const ESTADO_CONFIG = {
  en_proceso:  { label: 'En proceso',  color: 'bg-orange-100 text-orange-700' },
  solucionado: { label: 'Solucionado', color: 'bg-green-100 text-green-700'  },
  cerrado:     { label: 'Cerrado',     color: 'bg-gray-100 text-gray-600'    },
  rechazado:   { label: 'Rechazado',   color: 'bg-red-100 text-red-600'      },
}

const PRIORIDAD_CONFIG = {
  alta:  { label: 'Alta',  color: 'bg-red-100 text-red-600'        },
  media: { label: 'Media', color: 'bg-yellow-100 text-yellow-700'  },
  baja:  { label: 'Baja',  color: 'bg-green-100 text-green-700'    },
}

function Badge({ config }) {
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}

function StatCard({ label, value, icon, iconBg }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-6 flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500 mb-1">{label}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg}`}>
        {icon}
      </div>
    </div>
  )
}

function getInitials(nombre) {
  if (!nombre) return '?'
  const parts = nombre.trim().split(' ')
  return parts.length >= 2
    ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    : parts[0][0].toUpperCase()
}

const COLORS = ['bg-blue-600', 'bg-purple-600', 'bg-teal-600', 'bg-orange-500', 'bg-pink-600']
function avatarColor(name = '') {
  return COLORS[name.charCodeAt(0) % COLORS.length]
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const [stats,     setStats]     = useState({ total: 0, en_proceso: 0, resueltos: 0, rechazado: 0 })
  const [recientes, setRecientes] = useState([])
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState('')

  useEffect(() => {
    getDashboardStats()
      .then(({ data }) => {
        setStats(data.stats)
        setRecientes(data.recientes)
      })
      .catch(() => setError('Error al cargar el dashboard.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <AppLayout>
      <div className="p-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-3 text-gray-400 text-sm mb-6">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          <span>Panel de Administración</span>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

        {error && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total recibidos" value={stats.total}
            iconBg="bg-blue-50"
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" className="w-6 h-6"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>}
          />
          <StatCard
            label="En proceso" value={stats.en_proceso}
            iconBg="bg-orange-50"
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>}
          />
          <StatCard
            label="Resueltos" value={stats.resueltos}
            iconBg="bg-green-50"
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2" className="w-6 h-6"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>}
          />
          <StatCard
            label="Rechazados" value={stats.rechazado}
            iconBg="bg-red-50"
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" className="w-6 h-6"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>}
          />
        </div>

        {/* Tabla */}
        <div className="bg-white rounded-2xl border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Tickets Recientes</h2>
          </div>

          {loading ? (
            <div className="p-12 text-center text-gray-400 text-sm">Cargando...</div>
          ) : recientes.length === 0 ? (
            <div className="p-12 text-center text-gray-400 text-sm">No hay tickets aún.</div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-xs font-medium text-gray-500 px-6 py-3"># Ticket</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Prioridad</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Contenido</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Fecha y hora</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Estado</th>
                  <th className="text-left text-xs font-medium text-gray-500 px-4 py-3">Agente</th>
                </tr>
              </thead>
              <tbody>
                {recientes.map((ticket) => {
                  const agente = ticket.agente_asignado_nombre
                  const fecha  = new Date(ticket.created_at)
                  const fechaStr = `${fecha.getFullYear()}-${String(fecha.getMonth()+1).padStart(2,'0')}-${String(fecha.getDate()).padStart(2,'0')}`
                  const horaStr  = `${String(fecha.getHours()).padStart(2,'0')}:${String(fecha.getMinutes()).padStart(2,'0')}:00`

                  return (
                    <tr
                      key={ticket.id}
                      onClick={() => navigate(`/tickets/${ticket.id}`)}
                      className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {ticket.codigo_ticket}
                      </td>
                      <td className="px-4 py-4">
                        <Badge config={PRIORIDAD_CONFIG[ticket.prioridad] || { label: ticket.prioridad, color: 'bg-gray-100 text-gray-600' }} />
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-600 max-w-xs truncate">
                        {ticket.solicitud?.descripcion || '—'}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-500">
                        <div>{fechaStr}</div>
                        <div className="text-xs text-gray-400">{horaStr}</div>
                      </td>
                      <td className="px-4 py-4">
                        <Badge config={ESTADO_CONFIG[ticket.estado] || { label: ticket.estado, color: 'bg-gray-100 text-gray-600' }} />
                      </td>
                      <td className="px-4 py-4">
                        {agente ? (
                          <div className="flex items-center gap-2">
                            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold ${avatarColor(agente)}`}>
                              {getInitials(agente)}
                            </div>
                            <span className="text-sm text-gray-700">{agente}</span>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400">Sin asignar</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </AppLayout>
  )
}