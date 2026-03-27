import client from './client.js'

export function submitContactForm(payload) {
  return client.post('/api/v1/contact/', payload)
}
