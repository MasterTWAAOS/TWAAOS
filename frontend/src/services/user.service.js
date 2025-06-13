import apiClient from './api.service'

class UserService {
  /**
   * Get all users
   * @param {Object} params - Filter parameters
   * @returns {Promise} API Response
   */
  getAllUsers(params) {
    return apiClient.get('/admin/users', { params })
  }
  
  /**
   * Get user by ID
   * @param {number} id - User ID
   * @returns {Promise} API Response
   */
  getUserById(id) {
    return apiClient.get(`/admin/users/${id}`)
  }
  
  /**
   * Create new user
   * @param {Object} user - User data
   * @returns {Promise} API Response
   */
  createUser(user) {
    return apiClient.post('/admin/users', user)
  }
  
  /**
   * Update existing user
   * @param {number} id - User ID
   * @param {Object} user - User data
   * @returns {Promise} API Response
   */
  updateUser(id, user) {
    return apiClient.put(`/admin/users/${id}`, user)
  }
  
  /**
   * Delete user
   * @param {number} id - User ID
   * @returns {Promise} API Response
   */
  deleteUser(id) {
    return apiClient.delete(`/admin/users/${id}`)
  }
  
  /**
   * Toggle user status (activate/deactivate)
   * @param {number} id - User ID
   * @returns {Promise} API Response
   */
  toggleUserStatus(id) {
    return apiClient.put(`/admin/users/${id}/toggle-status`)
  }
  
  /**
   * Import users from file
   * @param {FormData} formData - Form data with file and options
   * @returns {Promise} API Response
   */
  importUsers(formData) {
    return apiClient.post('/admin/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  /**
   * Get users by role
   * @param {string} role - User role (e.g., 'CD', 'SG', 'ADMIN')
   * @param {Object} params - Additional query parameters (e.g., groupId)
   * @returns {Promise} API Response
   */
  getUsersByRole(role, params = {}) {
    return apiClient.get(`/users`, { 
      params: { 
        role: role,
        ...params 
      } 
    })
  }
}

export default new UserService()
