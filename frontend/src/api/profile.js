import client from './client.js'

export function getProfile() {
  return client.get('/api/v1/me/')
}

export function updateProfile(payload) {
  return client.patch('/api/v1/me/', payload)
}

export function changePassword(payload) {
  return client.post('/api/v1/me/change-password/', payload)
}
