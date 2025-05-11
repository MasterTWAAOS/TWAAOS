import axios from 'axios'

/**
 * Service for handling data synchronization with Flask API
 */
class SyncService {
  /**
   * Fetch and synchronize all data from USV APIs
   * @returns {Promise} Promise object representing the sync operation result
   */
  syncAll() {
    return axios.post('/api/flask/fetch-and-sync-data')
  }
  
  /**
   * Synchronize only groups data from USV APIs
   * @returns {Promise} Promise object representing the sync operation result
   */
  syncGroups() {
    return axios.post('/api/flask/sync/groups')
  }
  
  /**
   * Synchronize only rooms data from USV APIs
   * @returns {Promise} Promise object representing the sync operation result
   */
  syncRooms() {
    return axios.post('/api/flask/sync/rooms')
  }
  
  /**
   * Synchronize only faculty staff (professors) data from USV APIs
   * @returns {Promise} Promise object representing the sync operation result
   */
  syncFacultyStaff() {
    return axios.post('/api/flask/sync/faculty-staff')
  }
  
  /**
   * Get synchronization statistics
   * @returns {Promise} Promise object representing the sync stats data
   */
  getSyncStats() {
    return axios.get('/api/flask/sync/stats')
  }
  
  /**
   * Get the last synchronization timestamp
   * @returns {Promise} Promise object representing the last sync info
   */
  getLastSyncInfo() {
    return axios.get('/api/flask/sync/last-sync')
  }
}

export default new SyncService()
