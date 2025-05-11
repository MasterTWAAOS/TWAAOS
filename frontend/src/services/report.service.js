import apiClient from './api.service'

class ReportService {
  /**
   * Generate a standard predefined report
   * @param {string} reportType - Type of report to generate
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @returns {Promise} API Response with report URL
   */
  generateReport(reportType, format) {
    return apiClient.get(`/reports/generate/${reportType}`, {
      params: { format }
    })
  }

  /**
   * Generate a custom report based on specified parameters
   * @param {Object} params - Report parameters
   * @param {string} params.title - Report title
   * @param {string} params.type - Report type
   * @param {string} params.startDate - Start date (YYYY-MM-DD)
   * @param {string} params.endDate - End date (YYYY-MM-DD)
   * @param {Array} params.groups - Array of group IDs (optional)
   * @param {string} params.format - Format of report (pdf, xlsx, csv)
   * @returns {Promise} API Response with report URL
   */
  generateCustomReport(params) {
    return apiClient.post('/reports/custom', params)
  }

  /**
   * Get list of recently generated reports
   * @param {number} limit - Number of reports to return (default 5)
   * @returns {Promise} API Response with list of reports
   */
  getRecentReports(limit = 5) {
    return apiClient.get('/reports/recent', {
      params: { limit }
    })
  }

  /**
   * Download a previously generated report by ID
   * @param {number} reportId - Report ID
   * @returns {Promise} API Response with report binary data
   */
  downloadReport(reportId) {
    return apiClient.get(`/reports/download/${reportId}`, {
      responseType: 'blob'
    })
  }

  /**
   * Generate exam schedule report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateExamScheduleReport(format, filters = {}) {
    return apiClient.post('/reports/exam-schedule', {
      format,
      ...filters
    })
  }

  /**
   * Generate student lists report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateStudentListsReport(format, filters = {}) {
    return apiClient.post('/reports/student-lists', {
      format,
      ...filters
    })
  }

  /**
   * Generate room occupancy report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateRoomOccupancyReport(format, filters = {}) {
    return apiClient.post('/reports/room-occupancy', {
      format,
      ...filters
    })
  }

  /**
   * Generate professors and subjects report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateProfessorSubjectsReport(format, filters = {}) {
    return apiClient.post('/reports/professor-subjects', {
      format,
      ...filters
    })
  }

  /**
   * Generate session statistics report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateSessionStatsReport(format, filters = {}) {
    return apiClient.post('/reports/session-stats', {
      format,
      ...filters
    })
  }

  /**
   * Generate conflicts and overlaps report
   * @param {string} format - Format of report (pdf, xlsx, csv)
   * @param {Object} filters - Optional filters
   * @returns {Promise} API Response with report URL
   */
  generateConflictsReport(format, filters = {}) {
    return apiClient.post('/reports/conflicts', {
      format,
      ...filters
    })
  }

  /**
   * Generate attendance sheet for specific exam
   * @param {number} examId - Exam ID
   * @returns {Promise} API Response with attendance sheet URL
   */
  generateAttendanceSheet(examId) {
    return apiClient.get(`/reports/attendance-sheet/${examId}`)
  }
}

export default new ReportService()
