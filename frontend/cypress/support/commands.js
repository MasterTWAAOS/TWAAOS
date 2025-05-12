// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// -- Mock Google Auth for our FIESC exam scheduling application --
Cypress.Commands.add('loginWithGoogle', (userType) => {
  // This command handles the FIESC dual-mode authentication system
  // which uses email|role|groupId as mock token format in development mode
  
  cy.visit('/auth/login')
  cy.log(`Attempting Google login as ${userType}`)
  
  // Create mock token based on user type
  let mockToken;
  switch(userType) {
    case 'student':
      mockToken = 'student1@student.usv.ro|SG|914';
      break;
    case 'professor':
      mockToken = 'professor@usv.ro|CD|null';
      break;
    case 'secretary':
      mockToken = 'secretary@usv.ro|SEC|null';
      break;
    default:
      mockToken = 'student1@student.usv.ro|SG|914'; // Default to student
  }
  
  // Give app time to load and store token in localStorage
  cy.wait(2000)
  
  // Direct API approach which is most reliable for testing
  cy.request({
    method: 'POST',
    url: '/api/auth/google',
    body: { token: mockToken },
    failOnStatusCode: false,
  }).then(response => {
    cy.log(`API response status: ${response.status}`)
    
    if (response.status === 200 && response.body && response.body.token) {
      // If we got a token, set it and redirect
      cy.window().then(win => {
        cy.log('Setting token in localStorage')
        win.localStorage.setItem('token', response.body.token)
        win.location.href = '/'
      })
    } else {
      // If API call fails, try UI approach
      cy.log('API approach failed, trying UI interaction')
      cy.get('#googleSignInButton button').click({ force: true })
      
      // For dev mode, check if dialog appears and interact with it
      cy.wait(1000)
      cy.get('body').then($body => {
        const hasDialog = $body.find('[role="dialog"], .modal, .dialog, .p-dialog').length > 0
        
        if (hasDialog) {
          cy.log('Dialog found - selecting user type')
          // Try to find and click the option matching our user type
          cy.contains(new RegExp(userType, 'i'), { timeout: 5000 })
            .click({ force: true })
        } else {
          // Last resort: use window state
          cy.window().then(win => {
            cy.log('Using window state to set Google token')
            if (win.app && win.app.$store) {
              win.app.$store.dispatch('auth/loginWithGoogle', mockToken)
            } else {
              win.localStorage.setItem('mockGoogleToken', mockToken)
              // Reload to trigger auth
              win.location.reload()
            }
          })
        }
      })
    }
  })
  
  // Wait for authentication to complete
  cy.wait(5000) // Give enough time for redirect and rendering
  
  // Verify we're not on the login page anymore
  cy.url().should('not.include', '/auth/login', { timeout: 15000 })
  
  // Look for any navigation element that would indicate successful login
  cy.get('nav, .sidebar, header, .navigation-drawer, .v-navigation-drawer, .v-app-bar', { timeout: 15000 })
    .should('be.visible')
})

// -- Admin Login Command --
Cypress.Commands.add('loginAsAdmin', () => {
  cy.visit('/auth/login')
  
  // Direct API approach which is more reliable than UI interaction
  cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: {
      email: 'a@usv.ro',
      password: 'admin123'
    },
    failOnStatusCode: false
  }).then(response => {
    // Log for debugging
    cy.log(`API response status: ${response.status}`)
    
    if (response.status === 200 && response.body.token) {
      // If we get a token, set it and redirect
      cy.window().then(win => {
        win.localStorage.setItem('token', response.body.token)
        win.location.href = '/'
      })
    } else {
      // Fallback to UI login if API call fails
      cy.get('#username').type('a@usv.ro')
      cy.get('#password').type('admin123')
      cy.get('button[type="submit"]').click({ force: true })
    }
  })
  
  // Wait for redirect and dashboard to load
  cy.wait(3000) // Give time for routing
  cy.url().should('not.include', '/auth/login', { timeout: 15000 })
})
