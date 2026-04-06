import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import api from '../../api/axios'

const ESTADO_CONFIG = {
  en_proceso:  { label: 'En proceso',  color: 'bg-orange-100 text-orange-700 border border-orange-200' },
  solucionado: { label: 'Solucionado', color: 'bg-green-100 text-green-700 border border-green-200'   },
  cerrado:     { label: 'Cerrado',     color: 'bg-gray-100 text-gray-600 border border-gray-200'      },
  rechazado:   { label: 'Rechazado',   color: 'bg-red-100 text-red-600 border border-red-200'         },
}

const PRIORIDAD_CONFIG = {
  alta:  { label: 'Alta',  color: 'bg-red-100 text-red-600 border border-red-200'          },
  media: { label: 'Media', color: 'bg-yellow-100 text-yellow-700 border border-yellow-200' },
  baja:  { label: 'Baja',  color: 'bg-green-100 text-green-700 border border-green-200'    },
}

const COLORS = ['bg-blue-600', 'bg-purple-600', 'bg-teal-600', 'bg-orange-500', 'bg-pink-600']
function avatarColor(name = '') {
  return COLORS[name.charCodeAt(0) % COLORS.length]
}
function getInitials(nombre = '') {
  const p = nombre.trim().split(' ')
  return p.length >= 2 ? `${p[0][0]}${p[1][0]}`.toUpperCase() : p[0][0].toUpperCase()
}

function Badge({ config }) {
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  )
}

// ── Modal rechazo ──
function ModalRechazo({ codigo, onConfirm, onCancel, loading }) {
  const [motivo, setMotivo] = useState('')
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 text-lg">Rechazar Ticket</h3>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          Indica el motivo del rechazo para el ticket <strong>{codigo}</strong>.
        </p>
        <textarea
          value={motivo}
          onChange={e => setMotivo(e.target.value)}
          placeholder="Motivo del rechazo..."
          rows={4}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="flex gap-3 mt-4 justify-end">
          <button onClick={onCancel}
            className="px-5 py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 transition">
            Cancelar
          </button>
          <button
            onClick={() => onConfirm(motivo)}
            disabled={!motivo.trim() || loading}
            className="px-5 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 disabled:bg-red-300 text-white text-sm font-medium transition">
            {loading ? 'Rechazando...' : 'Confirmar rechazo'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function TicketDetailPage() {
  const { id }   = useParams()
  const navigate = useNavigate()

  const [ticket, setTicket]         = useState(null)
  const [loading, setLoading]       = useState(true)
  const [saving, setSaving]         = useState(false)
  const [modalRechazo, setModalRechazo] = useState(false)

  const [estadoEdit,    setEstadoEdit]    = useState('')
  const [prioridadEdit, setPrioridadEdit] = useState('')

  useEffect(() => {
    api.get(`/tickets/${id}/`).then(({ data }) => {
      setTicket(data)
      setEstadoEdit(data.estado)
      setPrioridadEdit(data.prioridad)
    }).finally(() => setLoading(false))
  }, [id])

  const handleRechazar = async (motivo) => {
    setSaving(true)
    try {
      const { data } = await api.post(`/tickets/${id}/rechazar/`, { motivo })
      setTicket(data)
      setEstadoEdit(data.estado)
      setModalRechazo(false)
    } catch (e) {
      alert(e.response?.data?.detail || 'Error al rechazar.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="p-12 text-center text-gray-400 text-sm">Cargando ticket...</div>
      </AppLayout>
    )
  }

  if (!ticket) {
    return (
      <AppLayout>
        <div className="p-12 text-center text-gray-400 text-sm">Ticket no encontrado.</div>
      </AppLayout>
    )
  }

  const cliente    = ticket.solicitud?.cliente
  const agente     = ticket.agente_asignado_nombre
  const estadoCfg  = ESTADO_CONFIG[ticket.estado]    || { label: ticket.estado,    color: 'bg-gray-100 text-gray-600' }
  const priorCfg   = PRIORIDAD_CONFIG[ticket.prioridad] || { label: ticket.prioridad, color: 'bg-gray-100 text-gray-600' }

  return (
    <AppLayout>
      {modalRechazo && (
        <ModalRechazo
          codigo={ticket.codigo_ticket}
          onConfirm={handleRechazar}
          onCancel={() => setModalRechazo(false)}
          loading={saving}
        />
      )}

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(-1)}
              className="text-gray-400 hover:text-gray-600 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{ticket.codigo_ticket}</h1>
              <p className="text-sm text-gray-400">Detalle del ticket</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge config={estadoCfg} />
            <Badge config={priorCfg} />
          </div>
        </div>

        <div className="flex gap-6">
          {/* Columna principal */}
          <div className="flex-1 flex flex-col gap-6">

            {/* Información general */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <h2 className="font-semibold text-gray-900 mb-5">Información General</h2>
              <div className="grid grid-cols-3 gap-y-5">
                <div>
                  <p className="text-xs text-gray-400 mb-1">ID Ticket</p>
                  <p className="text-sm font-medium text-gray-900">#{ticket.id}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Estado</p>
                  <Badge config={estadoCfg} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Canal de origen</p>
                  <p className="text-sm text-gray-900 capitalize">
                    {ticket.solicitud?.canal?.nombre?.replace('_', ' ') || '—'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Prioridad</p>
                  <Badge config={priorCfg} />
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Área</p>
                  {ticket.area_nombre
                    ? <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">{ticket.area_nombre}</span>
                    : <span className="text-sm text-gray-400">Sin área</span>
                  }
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Creado</p>
                  <p className="text-sm text-gray-900">
                    {new Date(ticket.created_at).toLocaleString('es-BO')}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Última actualización</p>
                  <p className="text-sm text-gray-900">
                    {new Date(ticket.updated_at).toLocaleString('es-BO')}
                  </p>
                </div>
              </div>
            </div>

            {/* Solicitud */}
            <div className="bg-white rounded-2xl border border-gray-100 p-6">
              <h2 className="font-semibold text-gray-900 mb-4">Solicitud</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                {ticket.solicitud?.descripcion || '—'}
              </p>

              {ticket.solicitud?.adjuntos?.length > 0 && (
                <div className="mt-5">
                  <p className="text-xs text-gray-400 uppercase tracking-wider mb-3">
                    Archivos adjuntos ({ticket.solicitud.adjuntos.length})
                  </p>
                  <div className="flex flex-col gap-2">
                    {ticket.solicitud.adjuntos.map((adj) => (
                      <div key={adj.id}
                        className="flex items-center justify-between px-4 py-3 rounded-xl border border-gray-100 hover:bg-gray-50 transition">
                        <div className="flex items-center gap-3">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-gray-400">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                          </svg>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{adj.nombre_archivo}</p>
                            {adj.tamanio_bytes && (
                              <p className="text-xs text-gray-400">
                                {(adj.tamanio_bytes / 1024).toFixed(1)} KB
                              </p>
                            )}
                          </div>
                        </div>
                        <a href={adj.url_archivo} target="_blank" rel="noreferrer"
                          className="text-gray-400 hover:text-blue-600 transition">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                          </svg>
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Acciones */}
            {ticket.estado === 'en_proceso' && (
              <div className="bg-white rounded-2xl border border-gray-100 p-6">
                <h2 className="font-semibold text-gray-900 mb-5">Acciones</h2>
                <div className="flex gap-4 items-end flex-wrap">
                  <div className="flex-1 min-w-40">
                    <label className="block text-xs text-gray-500 mb-1.5">Cambiar estado</label>
                    <select value={estadoEdit} onChange={e => setEstadoEdit(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                      <option value="en_proceso">En proceso</option>
                      <option value="solucionado">Solucionado</option>
                    </select>
                  </div>
                  <div className="flex-1 min-w-40">
                    <label className="block text-xs text-gray-500 mb-1.5">Cambiar prioridad</label>
                    <select value={prioridadEdit} onChange={e => setPrioridadEdit(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                      <option value="baja">Baja</option>
                      <option value="media">Media</option>
                      <option value="alta">Alta</option>
                    </select>
                  </div>
                  <button
                    onClick={() => setModalRechazo(true)}
                    className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white text-sm font-medium rounded-xl transition-colors">
                    Rechazar ticket
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Columna lateral */}
          <div className="w-72 flex flex-col gap-4 shrink-0">

            {/* Cliente */}
            <div className="bg-white rounded-2xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-900 mb-4">Cliente</h3>
              {cliente ? (
                <>
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0 ${avatarColor(cliente.usuario?.nombres || '')}`}>
                      {getInitials(`${cliente.usuario?.nombres || ''} ${cliente.usuario?.apellidos || ''}`)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">
                        {cliente.usuario?.nombres} {cliente.usuario?.apellidos}
                      </p>
                      <p className="text-xs text-gray-400 capitalize">
                        {cliente.rol_institucion || 'cliente'}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col gap-3 text-sm">
                    <div>
                      <p className="text-xs text-gray-400 mb-0.5">Institución</p>
                      <p className="text-gray-900">{cliente.institucion || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-0.5">Sistema</p>
                      <p className="text-gray-900">
                        {ticket.solicitud?.sistema?.nombre || '—'}
                        {ticket.solicitud?.sistema?.version && ` v${ticket.solicitud.sistema.version}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-0.5">Correo</p>
                      <p className="text-gray-900 break-all">{cliente.usuario?.email || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-0.5">Celular</p>
                      <p className="text-gray-900">{cliente.usuario?.nro_celular || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-0.5">Telegram</p>
                      <p className="text-gray-900">{cliente.usuario?.user_telegram || 'No registrado'}</p>
                    </div>
                  </div>
                </>
              ) : <p className="text-sm text-gray-400">Sin cliente</p>}
            </div>

            {/* Asignación */}
            <div className="bg-white rounded-2xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-900 mb-4">Asignación</h3>
              <div className="flex flex-col gap-3 text-sm">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Área asignada</p>
                  {ticket.area_nombre
                    ? <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">{ticket.area_nombre}</span>
                    : <span className="text-gray-400">Sin área</span>
                  }
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-2">Agente responsable</p>
                  {agente ? (
                    <div className="flex items-center gap-2">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 ${avatarColor(agente)}`}>
                        {getInitials(agente)}
                      </div>
                      <span className="text-gray-900">{agente}</span>
                    </div>
                  ) : (
                    <span className="text-gray-400">Sin asignar</span>
                  )}
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </AppLayout>
  )
}