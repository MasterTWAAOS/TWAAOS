/// <reference types="cypress" />

describe('Login Debug', () => {
  it('should attempt direct API authentication', () => {
    // First visit the login page
    cy.visit('/auth/login')
    
    // Log what we're doing
    cy.log('Attempting direct API authentication')
    
    // Directly access the API to authenticate
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'a@usv.ro',
        password: 'admin123'
      },
      failOnStatusCode: false
    }).then(response => {
      cy.log(`API response status: ${response.status}`)
      cy.log(`API response body: ${JSON.stringify(response.body)}`)
      
      if (response.status === 200 && response.body.token) {
        // If we get a token, set it in localStorage
        cy.window().then(win => {
          win.localStorage.setItem('token', response.body.token)
          win.location.href = '/'
        })
        
        // Wait for navigation and check for success
        cy.wait(5000)
        cy.log('Current URL: ' + cy.url())
      }
    })
  })
  
  it('should attempt mock Google auth with various methods', () => {
    // Log what we're doing
    cy.visit('/auth/login')
    cy.log('Attempting mock Google auth')
    
    // Click the Google button if it exists
    cy.get('#googleSignInButton button').click({ force: true })
    
    // Try to log whatever dialog appears
    cy.wait(2000)
    cy.log('Checking for Google auth dialog')
    
    cy.get('body').then($body => {
      const hasDialog = $body.find('.dialog, .modal, [role="dialog"]').length > 0
      cy.log(`Dialog found: ${hasDialog}`)
      
      if (hasDialog) {
        cy.get('.dialog, .modal, [role="dialog"]').screenshot('google-auth-dialog')
      }
      
      // Try direct token approach
      cy.window().then(win => {
        // The token format we're trying is email|role|groupId
        const mockToken = 'student1@student.usv.ro|SG|914'
        cy.log(`Setting mock token: ${mockToken}`)
        
        win.localStorage.setItem('mockGoogleToken', mockToken)
        
        // If store is available, dispatch the action
        if (win.app && win.app.$store) {
          cy.log('Found Vue app with store - dispatching action')
          win.app.$store.dispatch('auth/loginWithGoogle', mockToken)
        } else {
          cy.log('No Vue store found - using direct API call')
          // Try direct API call
          cy.request({
            method: 'POST',
            url: '/api/auth/google',
            body: { token: mockToken },
            failOnStatusCode: false
          }).then(response => {
            cy.log(`Google API response status: ${response.status}`)
            cy.log(`Google API response body: ${JSON.stringify(response.body)}`)
            
            if (response.status === 200 && response.body.token) {
              win.localStorage.setItem('token', response.body.token)
              win.location.href = '/'
            }
          })
        }
      })
    })
    
    // Wait and log results
    cy.wait(5000)
    cy.url().then(url => {
      cy.log(`Final URL: ${url}`)
    })
  })
})
