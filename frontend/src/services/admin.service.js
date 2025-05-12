import apiClient from './api.service'

class AdminService {
  /**
   * Get system statistics
   * @returns {Promise} API Response
   */
  getSystemStats() {
    return apiClient.get('/admin/stats')
  }

  /**
   * Get recent activity
   * @param {number} limit - Number of activities to retrieve
   * @returns {Promise} API Response
   */
  getRecentActivity(limit = 10) {
    return apiClient.get('/admin/activity', { params: { limit } })
  }

  /**
   * Get system alerts
   * @returns {Promise} API Response
   */
  getSystemAlerts() {
    return apiClient.get('/admin/alerts')
  }
  
  /**
   * Synchronize data from USV API
   * This calls the /api/sync/data endpoint in the FastAPI backend
   * which then triggers the Flask sync service and creates test users
   * @returns {Promise} API Response
   */
  syncData() {
    return apiClient.post('/sync/data')
  }

  /**
   * Dismiss system alert
   * @param {number} alertId - Alert ID
   * @returns {Promise} API Response
   */
  dismissAlert(alertId) {
    return apiClient.delete(`/admin/alerts/${alertId}`)
  }

  /**
   * Create system backup
   * @param {Object} backupData - Backup parameters
   * @returns {Promise} API Response
   */
  createBackup(backupData) {
    return apiClient.post('/admin/backup', backupData)
  }

  /**
   * Get system logs
   * @param {Object} params - Filter parameters
   * @returns {Promise} API Response
   */
  getSystemLogs(params) {
    return apiClient.get('/admin/logs', { params })
  }

  /**
   * Trigger sync job with Flask synchronization service
   * Uses the sync controller endpoint in the FastAPI application
   * @returns {Promise} API Response
   */
  triggerSyncJob() {
    return apiClient.post('/api/sync/groups')
  }

  /**
   * Get sync status from the Flask synchronization service
   * @returns {Promise} API Response
   */
  getSyncStatus() {
    return apiClient.get('/api/sync/status')
  }

  /**
   * Get all faculties
   * @returns {Promise} API Response
   */
  getAllFaculties() {
    return apiClient.get('/admin/faculties')
  }

  /**
   * Get faculty by ID
   * @param {number} id - Faculty ID
   * @returns {Promise} API Response
   */
  getFacultyById(id) {
    return apiClient.get(`/admin/faculties/${id}`)
  }

  /**
   * Create faculty
   * @param {Object} faculty - Faculty data
   * @returns {Promise} API Response
   */
  createFaculty(faculty) {
    return apiClient.post('/admin/faculties', faculty)
  }

  /**
   * Update faculty
   * @param {number} id - Faculty ID
   * @param {Object} faculty - Faculty data
   * @returns {Promise} API Response
   */
  updateFaculty(id, faculty) {
    return apiClient.put(`/admin/faculties/${id}`, faculty)
  }

  /**
   * Delete faculty
   * @param {number} id - Faculty ID
   * @returns {Promise} API Response
   */
  deleteFaculty(id) {
    return apiClient.delete(`/admin/faculties/${id}`)
  }
}

export default new AdminService()
