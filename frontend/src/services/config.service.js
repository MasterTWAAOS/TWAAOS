import apiClient from './api.service';

class ConfigService {
  /**
   * Get current (latest) configuration
   * @returns {Promise} Promise object that resolves to the API response
   */
  getCurrentConfig() {
    return apiClient.get('/configs/current');
  }

  /**
   * Get all configurations
   * @returns {Promise} Promise object that resolves to the API response
   */
  getAllConfigs() {
    return apiClient.get('/configs');
  }

  /**
   * Get configuration by ID
   * @param {number} id - Configuration ID
   * @returns {Promise} Promise object that resolves to the API response
   */
  getConfigById(id) {
    return apiClient.get(`/configs/${id}`);
  }

  /**
   * Create a new configuration
   * @param {Object} configData - Configuration data
   * @param {Date} configData.startDate - Start date
   * @param {Date} configData.endDate - End date
   * @returns {Promise} Promise object that resolves to the API response
   */
  createConfig(configData) {
    // FastAPI expects Body parameters with snake_case names
    return apiClient.post('/configs', {
      start_date: configData.startDate,
      end_date: configData.endDate
    });
  }

  /**
   * Update an existing configuration
   * @param {number} id - Configuration ID
   * @param {Object} configData - Configuration data
   * @param {Date} [configData.startDate] - Optional start date
   * @param {Date} [configData.endDate] - Optional end date
   * @returns {Promise} Promise object that resolves to the API response
   */
  updateConfig(id, configData) {
    // FastAPI expects Body parameters with snake_case names
    const updateData = {};
    
    if (configData.startDate) {
      updateData.start_date = configData.startDate;
    }
    if (configData.endDate) {
      updateData.end_date = configData.endDate;
    }
    
    return apiClient.put(`/configs/${id}`, updateData);
  }

  /**
   * Delete a configuration
   * @param {number} id - Configuration ID
   * @returns {Promise} Promise object that resolves to the API response
   */
  deleteConfig(id) {
    return apiClient.delete(`/configs/${id}`);
  }
}

export default new ConfigService();
