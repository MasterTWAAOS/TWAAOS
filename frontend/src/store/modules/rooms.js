import apiClient from '@/services/api.service'

const state = {
  rooms: [],
  loading: false,
  error: null
}

const getters = {
  allRooms: (state) => state.rooms,
  roomById: (state) => (id) => state.rooms.find(room => room.id === id),
  roomsLoading: (state) => state.loading
}

const actions = {
  async fetchRooms({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/rooms')
      commit('SET_ROOMS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch rooms')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createRoom({ commit, dispatch }, roomData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/rooms', roomData)
      commit('ADD_ROOM', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create room')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateRoom({ commit }, { id, roomData }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/rooms/${id}`, roomData)
      commit('UPDATE_ROOM', { id, room: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update room')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteRoom({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await apiClient.delete(`/rooms/${id}`)
      commit('DELETE_ROOM', id)
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete room')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_ROOMS(state, rooms) {
    state.rooms = rooms
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  ADD_ROOM(state, room) {
    state.rooms.unshift(room)
  },
  UPDATE_ROOM(state, { id, room }) {
    const index = state.rooms.findIndex(r => r.id === id)
    if (index !== -1) {
      state.rooms.splice(index, 1, room)
    }
  },
  DELETE_ROOM(state, id) {
    state.rooms = state.rooms.filter(room => room.id !== id)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
