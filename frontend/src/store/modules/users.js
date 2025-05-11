import apiClient from '@/services/api.service'

const state = {
  users: [],
  loading: false,
  error: null
}

const getters = {
  allUsers: (state) => state.users,
  userById: (state) => (id) => state.users.find(user => user.id === id),
  usersByRole: (state) => (role) => state.users.filter(user => user.role === role),
  usersLoading: (state) => state.loading
}

const actions = {
  async fetchUsers({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/admin/users')
      commit('SET_USERS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch users')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createUser({ commit }, userData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/admin/users', userData)
      commit('ADD_USER', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create user')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateUser({ commit }, { id, userData }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/admin/users/${id}`, userData)
      commit('UPDATE_USER', { id, user: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update user')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteUser({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await apiClient.delete(`/admin/users/${id}`)
      commit('DELETE_USER', id)
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete user')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async toggleUserStatus({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/admin/users/${id}/toggle-status`)
      commit('UPDATE_USER', { id, user: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to toggle user status')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async importUsers({ commit, dispatch }, formData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/admin/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // Refresh the users list after import
      await dispatch('fetchUsers')
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to import users')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_USERS(state, users) {
    state.users = users
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  ADD_USER(state, user) {
    state.users.unshift(user)
  },
  UPDATE_USER(state, { id, user }) {
    const index = state.users.findIndex(u => u.id === id)
    if (index !== -1) {
      state.users.splice(index, 1, user)
    }
  },
  DELETE_USER(state, id) {
    state.users = state.users.filter(user => user.id !== id)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
