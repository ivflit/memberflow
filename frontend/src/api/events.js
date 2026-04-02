import client from './client.js'

export function getEvents(params) {
  return client.get('/api/v1/events/', { params })
}

export function getEvent(id) {
  return client.get(`/api/v1/events/${id}/`)
}

export function getCategories() {
  return client.get('/api/v1/events/categories/')
}

export function getAgenda() {
  return client.get('/api/v1/events/agenda/')
}
