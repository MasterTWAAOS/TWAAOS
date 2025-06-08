import axios from 'axios'
import apiClient from './api.service'

/**
 * Service for handling Excel template operations
 */
class ExcelTemplateService {
  /**
   * Get templates by type with optional name filter
   * @param {string} type - Template type (sg, cd, sali)
   * @param {string} name - Optional name filter
   * @returns {Promise} Promise with templates
   */
  getTemplatesByType(type, name = null) {
    const url = `/excel-templates/type/${type}`
    const params = name ? { name } : {}
    return apiClient.get(url, { params })
  }

  /**
   * Download template file by ID
   * @param {number} id - Template ID
   * @returns {Promise} Promise with blob data
   */
  async downloadTemplate(id) {
    try {
      const response = await apiClient.request({
        url: `/excel-templates/download/${id}`,
        method: 'GET',
        responseType: 'blob', // This is important for binary file downloading
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      });
      return response;
    } catch (error) {
      console.error('Error downloading template:', error);
      throw error;
    }
  }
}

const excelTemplateService = new ExcelTemplateService()
export default excelTemplateService
