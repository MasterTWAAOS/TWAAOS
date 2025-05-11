import examService from '@/services/exam.service'

export default {
  namespaced: true,
  state: {
    exams: [],
    proposedExams: [],
    pendingExams: [],
    confirmedExams: [],
    currentExam: null,
    loading: false,
    error: null
  },
  getters: {
    getAllExams: state => state.exams,
    getProposedExams: state => state.proposedExams,
    getPendingExams: state => state.pendingExams,
    getConfirmedExams: state => state.confirmedExams,
    getCurrentExam: state => state.currentExam,
    isLoading: state => state.loading,
    hasError: state => state.error !== null,
    getError: state => state.error
  },
  mutations: {
    SET_EXAMS(state, exams) {
      state.exams = exams
    },
    SET_PROPOSED_EXAMS(state, exams) {
      state.proposedExams = exams
    },
    SET_PENDING_EXAMS(state, exams) {
      state.pendingExams = exams
    },
    SET_CONFIRMED_EXAMS(state, exams) {
      state.confirmedExams = exams
    },
    SET_CURRENT_EXAM(state, exam) {
      state.currentExam = exam
    },
    ADD_EXAM(state, exam) {
      state.exams.push(exam)
    },
    UPDATE_EXAM(state, updatedExam) {
      const index = state.exams.findIndex(exam => exam.id === updatedExam.id)
      if (index !== -1) {
        state.exams.splice(index, 1, updatedExam)
      }
      
      // Also update in the appropriate category arrays
      if (updatedExam.status === 'PROPOSED') {
        const proposedIndex = state.proposedExams.findIndex(exam => exam.id === updatedExam.id)
        if (proposedIndex !== -1) {
          state.proposedExams.splice(proposedIndex, 1, updatedExam)
        } else {
          state.proposedExams.push(updatedExam)
          // Remove from other arrays if necessary
          state.pendingExams = state.pendingExams.filter(exam => exam.id !== updatedExam.id)
          state.confirmedExams = state.confirmedExams.filter(exam => exam.id !== updatedExam.id)
        }
      } else if (updatedExam.status === 'PENDING') {
        const pendingIndex = state.pendingExams.findIndex(exam => exam.id === updatedExam.id)
        if (pendingIndex !== -1) {
          state.pendingExams.splice(pendingIndex, 1, updatedExam)
        } else {
          state.pendingExams.push(updatedExam)
          // Remove from other arrays if necessary
          state.proposedExams = state.proposedExams.filter(exam => exam.id !== updatedExam.id)
          state.confirmedExams = state.confirmedExams.filter(exam => exam.id !== updatedExam.id)
        }
      } else if (updatedExam.status === 'CONFIRMED') {
        const confirmedIndex = state.confirmedExams.findIndex(exam => exam.id === updatedExam.id)
        if (confirmedIndex !== -1) {
          state.confirmedExams.splice(confirmedIndex, 1, updatedExam)
        } else {
          state.confirmedExams.push(updatedExam)
          // Remove from other arrays if necessary
          state.proposedExams = state.proposedExams.filter(exam => exam.id !== updatedExam.id)
          state.pendingExams = state.pendingExams.filter(exam => exam.id !== updatedExam.id)
        }
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  actions: {
    // Fetch all exams
    async fetchExams({ commit }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.getAll()
        commit('SET_EXAMS', response.data)
        
        // Categorize exams by status
        const proposed = response.data.filter(exam => exam.status === 'PROPOSED')
        const pending = response.data.filter(exam => exam.status === 'PENDING')
        const confirmed = response.data.filter(exam => exam.status === 'CONFIRMED')
        
        commit('SET_PROPOSED_EXAMS', proposed)
        commit('SET_PENDING_EXAMS', pending)
        commit('SET_CONFIRMED_EXAMS', confirmed)
        
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch exams')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Fetch exams for a specific group
    async fetchExamsByGroup({ commit }, groupId) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.getByGroup(groupId)
        commit('SET_EXAMS', response.data)
        
        // Categorize exams by status
        const proposed = response.data.filter(exam => exam.status === 'PROPOSED')
        const pending = response.data.filter(exam => exam.status === 'PENDING')
        const confirmed = response.data.filter(exam => exam.status === 'CONFIRMED')
        
        commit('SET_PROPOSED_EXAMS', proposed)
        commit('SET_PENDING_EXAMS', pending)
        commit('SET_CONFIRMED_EXAMS', confirmed)
        
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch exams for group')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Fetch exams for a specific professor
    async fetchExamsByProfessor({ commit }, professorId) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.getByProfessor(professorId)
        commit('SET_EXAMS', response.data)
        
        // Categorize exams by status
        const proposed = response.data.filter(exam => exam.status === 'PROPOSED')
        const pending = response.data.filter(exam => exam.status === 'PENDING')
        const confirmed = response.data.filter(exam => exam.status === 'CONFIRMED')
        
        commit('SET_PROPOSED_EXAMS', proposed)
        commit('SET_PENDING_EXAMS', pending)
        commit('SET_CONFIRMED_EXAMS', confirmed)
        
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch exams for professor')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Propose exam date (student group leader)
    async proposeExamDate({ commit }, examData) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.proposeDate(examData)
        commit('ADD_EXAM', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to propose exam date')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Review proposed exam date (professor)
    async reviewExamProposal({ commit }, { examId, approved, feedback }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.reviewProposal(examId, approved, feedback)
        commit('UPDATE_EXAM', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to review exam proposal')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Set exam details (professor)
    async setExamDetails({ commit }, { examId, details }) {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      try {
        const response = await examService.setExamDetails(examId, details)
        commit('UPDATE_EXAM', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.message || 'Failed to set exam details')
        commit('SET_LOADING', false)
        throw error
      }
    },
    
    // Clear error
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    }
  }
}
