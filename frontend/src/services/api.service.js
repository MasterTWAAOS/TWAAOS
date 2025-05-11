import axios from 'axios'
import store from '@/store'
import router from '@/router'

// Create axios instance with base configurations
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for API calls
apiClient.interceptors.request.use(
  config => {
    const token = store.getters['auth/token']
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    Promise.reject(error)
  }
)

// Response interceptor for API calls
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Handle 401 (Unauthorized) - redirect to login
    if (error.response && error.response.status === 401) {
      store.dispatch('auth/logout')
      router.push('/auth/login')
    }
    
    // Handle 403 (Forbidden) - show access denied
    if (error.response && error.response.status === 403) {
      store.dispatch('setGlobalError', {
        type: 'access_denied',
        message: 'Access denied. You do not have permission to perform this action.'
      })
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
