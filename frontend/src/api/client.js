import axios from 'axios'

const client = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-Slug': import.meta.env.VITE_TENANT_SLUG || 'test-club',
  },
})

export default client
