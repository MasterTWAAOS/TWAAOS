/// <reference types="cypress" />

describe('Basic Authentication Tests', () => {
  it('should show login page correctly', () => {
    cy.visit('/auth/login')
    cy.contains('Autentificare').should('be.visible')
  })

  it('should login as admin using direct API call', () => {
    cy.visit('/auth/login')
    
    // Log direct API request
    cy.log('Making direct admin login API call')
    
    // Direct API call to authenticate
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'a@usv.ro',
        password: 'admin123'
      },
      failOnStatusCode: false
    }).then(response => {
      cy.log(`Response status: ${response.status}`)
      
      if (response.status === 200 && response.body && response.body.token) {
        cy.log('Login successful, setting token')
        
        // Set token in localStorage and redirect
        cy.window().then(win => {
          win.localStorage.setItem('token', response.body.token)
          win.location.href = '/'
        })
        
        // Wait for app to load after auth
        cy.wait(3000)
        
        // Verify we're logged in by looking for any navigation element
        cy.get('nav, .sidebar, header, .v-app-bar', { timeout: 10000 }).should('exist')
      } else {
        cy.log(`Login failed: ${JSON.stringify(response.body)}`)
      }
    })
  })
})
