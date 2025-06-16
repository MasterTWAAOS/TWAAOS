import apiClient from '@/services/api.service'

const state = {
  examSchedules: [],
  examPeriods: [],
  loading: false,
  error: null
}

const getters = {
  allExamSchedules: (state) => state.examSchedules,
  allExamPeriods: (state) => state.examPeriods,
  activeExamPeriods: (state) => state.examPeriods.filter(period => 
    new Date(period.endDate) >= new Date()
  ),
  currentExamPeriod: (state) => {
    const now = new Date()
    return state.examPeriods.find(period => 
      new Date(period.startDate) <= now && new Date(period.endDate) >= now
    )
  },
  schedulesLoading: (state) => state.loading
}

const actions = {
  async fetchExamSchedules({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/schedules')
      commit('SET_EXAM_SCHEDULES', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch exam schedules')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchExamPeriods({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/periods')
      commit('SET_EXAM_PERIODS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch exam periods')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createExamPeriod({ commit, dispatch }, periodData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/periods', periodData)
      commit('ADD_EXAM_PERIOD', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create exam period')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateExamPeriod({ commit }, { id, periodData }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/periods/${id}`, periodData)
      commit('UPDATE_EXAM_PERIOD', { id, period: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update exam period')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteExamPeriod({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await apiClient.delete(`/periods/${id}`)
      commit('DELETE_EXAM_PERIOD', id)
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete exam period')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createScheduleEntry({ commit, dispatch }, scheduleData) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.post('/schedules', scheduleData)
      commit('ADD_EXAM_SCHEDULE', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to create schedule entry')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateScheduleEntry({ commit }, { id, scheduleData }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.put(`/schedules/${id}`, scheduleData)
      commit('UPDATE_EXAM_SCHEDULE', { id, schedule: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to update schedule entry')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // CD (Course Director) specific actions for handling exam proposals
  async fetchProposals({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await apiClient.get('/schedules?status=proposed')
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch proposals')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchCDProposals({ commit, rootState }) {
    try {
      commit('SET_LOADING', true)
      // Get current user info to identify CD's subjects
      const currentUser = rootState.auth.user
      
      if (!currentUser || !currentUser.id) {
        throw new Error('User not authenticated')
      }
      
      // Use our new endpoint that directly gets schedules for the CD's subjects with proposed status
      // This is much more efficient as it does the filtering on the server side
      const response = await apiClient.get(`/schedules/teacher/${currentUser.id}?status=proposed`)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to fetch CD proposals')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async approveProposal({ commit }, { scheduleId, approvalData }) {
    try {
      commit('SET_LOADING', true)
      // Handle both formats: either approvalData with roomId + additionalRoomIds or just roomIds
      const updateData = {
        status: 'approved',
        roomId: approvalData.roomId || (approvalData.roomIds && approvalData.roomIds[0]), // Primary room
        additionalRoomIds: approvalData.additionalRoomIds || (approvalData.roomIds ? approvalData.roomIds.slice(1) : []), // Additional rooms if any
        assistantIds: approvalData.assistantIds,
        startTime: approvalData.startTime,
        endTime: approvalData.endTime,
        comments: approvalData.comments,
        sendEmail: approvalData.sendEmail || true // Ensure sendEmail is always passed
      }
      
      console.log('Sending approval data to API:', updateData);
      
      const response = await apiClient.put(`/schedules/${scheduleId}`, updateData)
      commit('UPDATE_EXAM_SCHEDULE', { id: scheduleId, schedule: response.data })
      return response.data
    } catch (error) {
      console.error('Error in approveProposal:', error);
      commit('SET_ERROR', error.message || 'Failed to approve proposal')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async rejectProposal({ commit }, { scheduleId, rejectionData }) {
    try {
      commit('SET_LOADING', true)
      const updateData = {
        status: 'rejected',
        reason: rejectionData.reason,
        sendEmail: rejectionData.sendEmail || true
      }
      
      const response = await apiClient.put(`/schedules/${scheduleId}`, updateData)
      commit('UPDATE_EXAM_SCHEDULE', { id: scheduleId, schedule: response.data })
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to reject proposal')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async checkConflicts({ commit }, conflictData) {
    try {
      const response = await apiClient.post('/schedules/check-conflicts', conflictData)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to check for conflicts')
      throw error
    }
  },

  async deleteScheduleEntry({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await apiClient.delete(`/schedules/${id}`)
      commit('DELETE_EXAM_SCHEDULE', id)
    } catch (error) {
      commit('SET_ERROR', error.message || 'Failed to delete schedule entry')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_EXAM_SCHEDULES(state, schedules) {
    state.examSchedules = schedules
  },
  SET_EXAM_PERIODS(state, periods) {
    state.examPeriods = periods
  },
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  ADD_EXAM_SCHEDULE(state, schedule) {
    state.examSchedules.unshift(schedule)
  },
  UPDATE_EXAM_SCHEDULE(state, { id, schedule }) {
    const index = state.examSchedules.findIndex(s => s.id === id)
    if (index !== -1) {
      state.examSchedules.splice(index, 1, schedule)
    }
  },
  DELETE_EXAM_SCHEDULE(state, id) {
    state.examSchedules = state.examSchedules.filter(schedule => schedule.id !== id)
  },
  ADD_EXAM_PERIOD(state, period) {
    state.examPeriods.unshift(period)
  },
  UPDATE_EXAM_PERIOD(state, { id, period }) {
    const index = state.examPeriods.findIndex(p => p.id === id)
    if (index !== -1) {
      state.examPeriods.splice(index, 1, period)
    }
  },
  DELETE_EXAM_PERIOD(state, id) {
    state.examPeriods = state.examPeriods.filter(period => period.id !== id)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
