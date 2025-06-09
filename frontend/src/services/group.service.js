import apiClient from './api.service'

class GroupService {
  /**
   * Get all study groups with detailed information
   * @returns {Promise<Array>} Promise that resolves to an array of group objects
   */
  async getAllGroups() {
    // The backend endpoint for all groups is correctly /groups
    const response = await apiClient.get('/groups')
    return response.data
  }

  /**
   * Get group by ID
   * @param {number} id - Group ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/groups/${id}`)
  }
}

export default new GroupService()
