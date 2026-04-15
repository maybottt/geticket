import api from './axios'

export const login = (credentials) =>
  api.post('/auth/login/', credentials)

export const elegirRol = (user_id, rol) =>
  api.post('/auth/elegir-rol/', { user_id, rol })

export const switchRol = (rol) =>
  api.post('/auth/switch-rol/', { rol })

export const getMe = () =>
  api.get('/auth/me/')

export const changePassword = (data) =>
  api.post('/auth/change-password/', data)

export const registroCliente = (data) =>
  api.post('/auth/registro/cliente/', data)

export const getInstituciones = () =>
  api.get('/instituciones/')