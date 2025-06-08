import apiClient from './api.service'

class RoomService {
  /**
   * Get all rooms with detailed information
   * @returns {Promise<Array>} Promise that resolves to an array of room objects
   */
  async getAllRooms() {
    const response = await apiClient.get('/rooms')
    return response.data
  }

  /**
   * Get room by ID
   * @param {number} id - Room ID
   * @returns {Promise} API Response
   */
  getById(id) {
    return apiClient.get(`/rooms/${id}`)
  }

  /**
   * Get rooms by building
   * @param {string} buildingName - Building name
   * @returns {Promise} API Response
   */
  getByBuilding(buildingName) {
    return apiClient.get(`/rooms/building/${buildingName}`)
  }

  /**
   * Generate Excel file with room information
   * @returns {Promise} API Response with Excel file as blob
   */
  generateRoomExcel() {
    return apiClient.get('/excel-templates/rooms/generate-excel', {
      responseType: 'blob',
      headers: {
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
    })
  }
}

export default new RoomService()
