import apiClient from '@/services/api.service'

const state = {
  groups: [],
  loading: false,
  error: null,
  syncStatus: {
    lastSync: null,
    inProgress: false,
    error: null
  }
}

const getters = {
  allGroups: (state) => state.groups,
  groupById: (state) => (id) => state.groups.find(group => group.id === id),
  groupsByFaculty: (state) => (facultyId) => state.groups.filter(group => group.facultyId === facultyId),
  groupsLoading: (state) => state.loading,
  syncInProgress: (state) => state.syncStatus.inProgress,
  lastSyncDate: (state) => state.syncStatus.lastSync
}

const actions = {
  async fetchGroups({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/groups')
      commit('SET_GROUPS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch groups')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // This action connects to the Flask sync system you've created
  async syncGroupsWithUSV({ commit }) {
    try {
      commit('SET_SYNC_IN_PROGRESS', true)
      commit('SET_SYNC_ERROR', null)
      
      // Call the sync endpoint in FastAPI that connects to Flask sync service
      const response = await apiClient.post('/api/sync/groups')
      
      // Set the last sync date
      commit('SET_LAST_SYNC', new Date())
      
      // Fetch the updated groups
      await this.dispatch('groups/fetchGroups')
      
      return response.data
    } catch (error) {
      commit('SET_SYNC_ERROR', error.message || 'Failed to sync groups with USV')
      throw error
    } finally {
      commit('SET_SYNC_IN_PROGRESS', false)
    }
  },

  async getSyncStatus({ commit }) {
    try {
      const response = await apiClient.get('/api/sync/status')
      
      if (response.data.lastSync) {
        commit('SET_LAST_SYNC', new Date(response.data.lastSync))
      }
      
      return response.data
    } catch (error) {
      console.error('Error getting sync status:', error)
      throw error
    }
  },

  async createGroup({ commit }, groupData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/groups', groupData)
      commit('ADD_GROUP', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create group')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateGroup({ commit }, { id, groupData }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/groups/${id}`, groupData)
      commit('UPDATE_GROUP', { id, group: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update group')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteGroup({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await apiClient.delete(`/groups/${id}`)
      commit('DELETE_GROUP', id)
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete group')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_GROUPS(state, groups) {
    state.groups = groups
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  ADD_GROUP(state, group) {
    state.groups.unshift(group)
  },
  UPDATE_GROUP(state, { id, group }) {
    const index = state.groups.findIndex(g => g.id === id)
    if (index !== -1) {
      state.groups.splice(index, 1, group)
    }
  },
  DELETE_GROUP(state, id) {
    state.groups = state.groups.filter(group => group.id !== id)
  },
  SET_SYNC_IN_PROGRESS(state, status) {
    state.syncStatus.inProgress = status
  },
  SET_LAST_SYNC(state, date) {
    state.syncStatus.lastSync = date
  },
  SET_SYNC_ERROR(state, error) {
    state.syncStatus.error = error
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
