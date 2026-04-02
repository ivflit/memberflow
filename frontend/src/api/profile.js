import client from './client.js'

export function getProfile() {
  return client.get('/api/v1/profile/')
}

export function updateProfile(payload) {
  return client.patch('/api/v1/profile/', payload)
}

export function changePassword(payload) {
  return client.post('/api/v1/profile/change-password/', payload)
}
