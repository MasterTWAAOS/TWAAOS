import apiClient from './api.service'

class ScheduleService {
  /**
   * Get all schedules with optional filtering
   * @param {Object} filters - Filter parameters (status, date, subjectId, etc.)
   * @returns {Promise} API Response
   */
  getAllSchedules(filters = {}) {
    // Convert filters object to query string
    const queryParams = new URLSearchParams()
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value)
      }
    })
    
    const queryString = queryParams.toString()
    const url = queryString ? `/schedules?${queryString}` : '/schedules'
    
    return apiClient.get(url)
  }

  /**
   * Get schedule by ID
   * @param {number} id - Schedule ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/schedules/${id}`)
  }

  /**
   * Get schedules for subjects where the user is the teacher
   * @param {number} teacherId - Teacher/CD user ID
   * @param {string} status - Optional filter by status
   * @returns {Promise} API Response
   */
  getTeacherSchedules(teacherId, status = null) {
    let url = `/schedules/teacher/${teacherId}`
    if (status) {
      url += `?status=${status}`
    }
    return apiClient.get(url)
  }
  
  /**
   * Update schedule status and details
   * @param {number} scheduleId - Schedule ID
   * @param {Object} updateData - Schedule update data
   * @returns {Promise} API Response
   */
  updateSchedule(scheduleId, updateData) {
    return apiClient.put(`/schedules/${scheduleId}`, updateData)
  }
  
  /**
   * Approve a proposed schedule with room, assistant assignments and time interval
   * @param {number} scheduleId - Schedule ID to approve
   * @param {Object} approvalData - Data for the approval
   * @returns {Promise} API Response
   */
  approveProposal(scheduleId, approvalData) {
    const updateData = {
      status: 'approved',
      roomId: approvalData.roomIds[0], // Primary room
      additionalRoomIds: approvalData.roomIds.slice(1), // Additional rooms
      assistantIds: approvalData.assistantIds,
      startTime: approvalData.startTime,
      endTime: approvalData.endTime,
      comments: approvalData.comments
    }
    
    return this.updateSchedule(scheduleId, updateData)
  }
  
  /**
   * Reject a proposed schedule with reason and optional email notification
   * @param {number} scheduleId - Schedule ID to reject
   * @param {string} reason - Reason for rejection
   * @param {boolean} sendEmail - Whether to send email notification
   * @returns {Promise} API Response
   */
  rejectProposal(scheduleId, reason, sendEmail = true) {
    const updateData = {
      status: 'rejected',
      reason: reason,
      sendEmail: sendEmail
    }
    
    return this.updateSchedule(scheduleId, updateData)
  }
  
  /**
   * Check for conflicts with existing schedules
   * @param {Object} conflictData - Data to check conflicts
   * @returns {Promise} API Response with conflicts
   */
  checkConflicts(conflictData) {
    return apiClient.post('/schedules/check-conflicts', conflictData)
  }
  
  /**
   * Get assistants (CD users) associated with a specific subject
   * @param {number} subjectId - Subject ID
   * @returns {Promise} API Response with assistant user data
   */
  getSubjectAssistants(subjectId) {
    return apiClient.get(`/schedules/assistants/${subjectId}`)
  }
}

export default new ScheduleService()
