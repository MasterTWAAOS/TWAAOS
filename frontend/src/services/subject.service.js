import apiClient from './api.service'

class SubjectService {
  /**
   * Get all subjects with detailed information
   * @returns {Promise<Array>} Promise that resolves to an array of subject objects
   */
  async getAllSubjects() {
    // The backend endpoint for all subjects is correctly /subjects
    const response = await apiClient.get('/subjects')
    return response.data
  }

  /**
   * Get subject by ID
   * @param {number} id - Subject ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/subjects/${id}`)
  }
  
  /**
   * Get subjects by teacher ID
   * @param {number} teacherId - Teacher ID
   * @returns {Promise<Array>} Promise that resolves to an array of subject objects
   */
  async getByTeacherId(teacherId) {
    const response = await apiClient.get(`/subjects/teacher/${teacherId}`)
    return response.data
  }
}

export default new SubjectService()
