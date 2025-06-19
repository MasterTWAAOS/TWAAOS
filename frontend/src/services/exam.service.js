import apiClient from './api.service'

class ExamService {
  /**
   * Get all exams with detailed information
   * @returns {Promise<Array>} Promise that resolves to an array of exam objects
   */
  async getAllExams() {
    const response = await apiClient.get('/exams')
    return response.data
  }

  /**
   * Get exam by ID
   * @param {number} id - Exam ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/exams/${id}`)
  }

  /**
   * Get exams for a specific group
   * @param {number} groupId - Group ID
   * @returns {Promise} API Response
   */
  getByGroup(groupId) {
    return apiClient.get(`/exams/group/${groupId}`)
  }

  /**
   * Get exams for a specific professor
   * @param {number} professorId - Professor ID
   * @returns {Promise} API Response
   */
  getByProfessor(professorId) {
    return apiClient.get(`/exams/professor/${professorId}`)
  }
  
  /**
   * Get dashboard data for a professor/teacher
   * @param {number} professorId - Professor ID
   * @returns {Promise} API Response with dashboard data including stats and upcoming exams
   */
  getTeacherDashboard(professorId) {
    return apiClient.get(`/exams/teacher/${professorId}/dashboard`)
  }

  /**
   * Propose a new exam date (student group leader)
   * @param {Object} examData - The exam data
   * @returns {Promise} API Response
   */
  proposeDate(examData) {
    return apiClient.post('/exams/propose', examData)
  }

  /**
   * Review a proposed exam date (professor)
   * @param {number} examId - Exam ID
   * @param {boolean} approved - Whether the proposal is approved
   * @param {string} feedback - Optional feedback
   * @returns {Promise} API Response
   */
  reviewProposal(examId, approved, feedback) {
    return apiClient.post(`/exams/${examId}/review`, {
      approved,
      feedback
    })
  }

  /**
   * Set exam details after approval (professor)
   * @param {number} examId - Exam ID
   * @param {Object} details - Exam details including room, assistants, time
   * @returns {Promise} API Response
   */
  setExamDetails(examId, details) {
    return apiClient.put(`/exams/${examId}/details`, details)
  }

  /**
   * Update exam information (secretariat)
   * @param {number} examId - Exam ID
   * @param {Object} examData - Updated exam data
   * @returns {Promise} API Response
   */
  updateExam(examId, examData) {
    return apiClient.put(`/exams/${examId}`, examData)
  }
  
  /**
   * Generate Excel file with exam information grouped by program, year, and group
   * with teacher email and contact details
   * @returns {Promise} API Response with Excel file as blob
   */
  generateExamExcel() {
    return apiClient.get('/excel-templates/exams/generate-excel', {
      responseType: 'blob',
      headers: {
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
    })
  }
}

export default new ExamService()
