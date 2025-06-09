import apiClient from './api.service'

class TeacherService {
  /**
   * Get all teachers (professors) with detailed information
   * @returns {Promise<Array>} Promise that resolves to an array of teacher objects
   */
  async getAllTeachers() {
    // Teachers are users with role 'CD' (Cadru Didactic)
    const response = await apiClient.get('/users', { params: { role: 'CD' } })
    return response.data
  }

  /**
   * Get teacher by ID
   * @param {number} id - Teacher ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/users/${id}`)
  }
}

export default new TeacherService()
