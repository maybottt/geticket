import api from './axios'

export const getDashboardStats = () => api.get('/dashboard/stats/')
export const getTickets        = (params) => api.get('/tickets/', { params })
export const getTicket         = (id) => api.get(`/tickets/${id}/`)
export const rechazarTicket    = (id, motivo) => api.post(`/tickets/${id}/rechazar/`, { motivo })
export const asignarTicket     = (id, agente_id) => api.post(`/tickets/${id}/asignar/`, { agente_id })
export const solucionarTicket  = (id, comentario) => api.post(`/tickets/${id}/solucionar/`, { comentario_solucion: comentario })
export const cerrarTicket      = (id) => api.post(`/tickets/${id}/cerrar/`)
export const confirmarTicket   = (id) => api.post(`/tickets/${id}/confirmar/`)
export const escalarTicket     = (id, agente_id, motivo) => api.post(`/tickets/${id}/escalar/`, { agente_id, motivo_escalamiento: motivo })