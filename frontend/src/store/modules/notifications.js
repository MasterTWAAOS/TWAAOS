/**
 * Vuex store module for managing application notifications using PrimeVue Toast
 */
const state = {
  notifications: []
}

const getters = {
  notifications: state => state.notifications
}

const actions = {
  /**
   * Show a notification using PrimeVue Toast
   * @param {Object} context - Vuex context
   * @param {Object} notification - Notification configuration
   * @param {string} notification.severity - Severity level ('success', 'info', 'warn', 'error')
   * @param {string} notification.summary - Notification title
   * @param {string} notification.detail - Notification message
   * @param {number} notification.life - Duration in milliseconds
   */
  showNotification({ commit }, notification) {
    // This doesn't use a mutation because the Toast component is accessed through the $toast service
    // and doesn't rely on the state directly
    
    if (window.$toast) {
      window.$toast.add({
        severity: notification.severity || 'info',
        summary: notification.summary || '',
        detail: notification.detail || '',
        life: notification.life || 3000
      })
    }
    
    // Add to notifications history if needed
    commit('ADD_NOTIFICATION', notification)
  },
  
  /**
   * Clear all notifications from history
   */
  clearNotifications({ commit }) {
    commit('CLEAR_NOTIFICATIONS')
  }
}

const mutations = {
  ADD_NOTIFICATION(state, notification) {
    // Add notification to history with timestamp
    state.notifications.push({
      ...notification,
      timestamp: new Date()
    })
    
    // Limit the history to last 50 notifications
    if (state.notifications.length > 50) {
      state.notifications.shift()
    }
  },
  
  CLEAR_NOTIFICATIONS(state) {
    state.notifications = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
