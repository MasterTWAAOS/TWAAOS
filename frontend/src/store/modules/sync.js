import axios from 'axios'

const state = {
  isSyncing: false,
  lastSyncDate: null,
  error: null,
  syncStats: {
    groups: 0,
    rooms: 0,
    professors: 0
  }
}

const getters = {
  isSyncing: state => state.isSyncing,
  lastSyncDate: state => state.lastSyncDate,
  syncError: state => state.error,
  syncStats: state => state.syncStats
}

const actions = {
  /**
   * Fetch and synchronize data from USV APIs through the Flask synchronization service
   */
  async fetchAndSyncData({ commit }) {
    commit('SET_SYNCING', true)
    commit('SET_ERROR', null)
    
    try {
      // Call the Flask API endpoint to trigger data synchronization
      const response = await axios.post('/api/flask/fetch-and-sync-data')
      
      // Update sync stats with the response data
      commit('SET_SYNC_STATS', response.data)
      
      // Update the last sync date
      commit('SET_LAST_SYNC_DATE', new Date())
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || error.message)
      throw error
    } finally {
      commit('SET_SYNCING', false)
    }
  },
  
  /**
   * Sync only groups data from USV APIs
   */
  async syncGroups({ commit }) {
    commit('SET_SYNCING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await axios.post('/api/flask/sync/groups')
      commit('SET_SYNC_STATS', { ...state.syncStats, groups: response.data.count })
      commit('SET_LAST_SYNC_DATE', new Date())
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || error.message)
      throw error
    } finally {
      commit('SET_SYNCING', false)
    }
  },
  
  /**
   * Sync only rooms data from USV APIs
   */
  async syncRooms({ commit }) {
    commit('SET_SYNCING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await axios.post('/api/flask/sync/rooms')
      commit('SET_SYNC_STATS', { ...state.syncStats, rooms: response.data.count })
      commit('SET_LAST_SYNC_DATE', new Date())
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || error.message)
      throw error
    } finally {
      commit('SET_SYNCING', false)
    }
  },
  
  /**
   * Sync only faculty staff (professors) data from USV APIs
   */
  async syncProfessors({ commit }) {
    commit('SET_SYNCING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await axios.post('/api/flask/sync/faculty-staff')
      commit('SET_SYNC_STATS', { ...state.syncStats, professors: response.data.count })
      commit('SET_LAST_SYNC_DATE', new Date())
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || error.message)
      throw error
    } finally {
      commit('SET_SYNCING', false)
    }
  },
  
  /**
   * Reset sync error
   */
  clearError({ commit }) {
    commit('SET_ERROR', null)
  }
}

const mutations = {
  SET_SYNCING(state, isSyncing) {
    state.isSyncing = isSyncing
  },
  
  SET_LAST_SYNC_DATE(state, date) {
    state.lastSyncDate = date
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  SET_SYNC_STATS(state, stats) {
    state.syncStats = { ...state.syncStats, ...stats }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
