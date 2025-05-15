import authService from '@/services/auth.service'
import router from '@/router'
import jwtDecode from 'jwt-decode'

const initialState = {
  token: localStorage.getItem('token') || null,
  user: null,
  loading: false,
  error: null
}

// Parse user from token if it exists
if (initialState.token) {
  try {
    const decodedToken = jwtDecode(initialState.token)
    initialState.user = {
      id: decodedToken.sub,
      firstName: decodedToken.firstName,
      lastName: decodedToken.lastName,
      email: decodedToken.email,
      role: decodedToken.role,
      groupId: decodedToken.groupId,
    }
  } catch (e) {
    // Invalid token, reset state
    initialState.token = null
    initialState.user = null
    localStorage.removeItem('token')
  }
}

export default {
  namespaced: true,
  state: initialState,
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    userRole: state => state.user ? state.user.role : null,
    authError: state => state.error,
    isLoading: state => state.loading
  },
  mutations: {
    LOGIN_REQUEST(state) {
      state.loading = true
      state.error = null
    },
    LOGIN_SUCCESS(state, { token, user }) {
      state.token = token
      state.user = user
      state.loading = false
      state.error = null
    },
    LOGIN_FAILURE(state, error) {
      state.loading = false
      state.error = error
    },
    LOGOUT(state) {
      state.token = null
      state.user = null
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  actions: {
    async loginWithGoogle({ commit }, googleToken) {
      commit('LOGIN_REQUEST')
      try {
        const response = await authService.googleLogin(googleToken)
        const { token, user } = response.data
        
        // Validate that the user role is appropriate for Google login
        if (user.role === 'ADM') {
          commit('LOGIN_FAILURE', 'Administrator accounts cannot use Google authentication. Please use username/password login.')
          return Promise.reject(new Error('Administrator accounts cannot use Google authentication'))
        }
        
        // Store token in localStorage
        localStorage.setItem('token', token)
        
        commit('LOGIN_SUCCESS', { token, user })
        
        // Redirect to appropriate dashboard based on user role
        if (user.role === 'SG') router.push('/student')
        else if (user.role === 'CD') router.push('/professor')
        else if (user.role === 'SEC') router.push('/secretariat')
        
        return response
      } catch (error) {
        commit('LOGIN_FAILURE', error.response?.data?.message || 'An error occurred during login')
        throw error
      }
    },
    
    loginWithCredentials({ commit }, { username, password }) {
      commit('LOGIN_REQUEST')
      return authService.login(username, password)
        .then(response => {
          const { token, user } = response.data
          
          // Validate that only Administrators can use username/password login
          if (user.role !== 'ADM') {
            commit('LOGIN_FAILURE', 'Non-administrator accounts must use Google authentication')
            return Promise.reject(new Error('Non-administrator accounts must use Google authentication'))
          }
          
          // Store token in localStorage
          localStorage.setItem('token', token)
          
          commit('LOGIN_SUCCESS', { token, user })
          
          // For Admin role, redirect to admin dashboard
          router.push('/admin')
          
          return response
        })
        .catch(error => {
          commit('LOGIN_FAILURE', error.response?.data?.message || 'Invalid credentials')
          throw error
        })
    },
    
    logout({ commit }) {
      localStorage.removeItem('token')
      commit('LOGOUT')
      router.push('/auth/login')
    },
    
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  }
}
