import apiClient from './api.service'

class AuthService {
  /**
   * Log in with Google token
   * @param {string} googleToken - The ID token from Google Sign-In
   * @returns {Promise} API Response
   */
  googleLogin(googleToken) {
    return apiClient.post('/auth/google', { token: googleToken })
  }

  /**
   * Log in with username/password (for admin users)
   * @param {string} username - The username
   * @param {string} password - The password
   * @returns {Promise} API Response
   */
  login(username, password) {
    return apiClient.post('/auth/login', { username, password })
  }

  /**
   * Change admin password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @returns {Promise} API Response
   */
  changePassword(currentPassword, newPassword) {
    return apiClient.post('/auth/change-password', { 
      currentPassword, 
      newPassword 
    })
  }
}

export default new AuthService()
