/// <reference types="cypress" />

describe('Authentication Tests', () => {
  beforeEach(() => {
    // Reset the application state before each test
    cy.visit('/')
  })

  it('should show the login page', () => {
    cy.url().should('include', '/auth/login')
    cy.contains('h2', 'Autentificare').should('be.visible')
    cy.contains('FIESC - Planificarea Examenelor').should('be.visible')
    cy.get('#googleSignInButton').should('be.visible')
  })

  it('should login as admin', () => {
    cy.loginAsAdmin()
    
    // Verify we're on the admin dashboard
    cy.contains('Dashboard', { timeout: 10000 }).should('be.visible')
    
    // Verify user info is displayed
    cy.contains('A A', { timeout: 10000 }).should('be.visible')
    
    // Log out
    cy.get('button[tooltip="Deconectare"]', { timeout: 10000 }).click({ force: true })
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
  })

  it('should login as student via Google auth', () => {
    cy.loginWithGoogle('student')
    
    // Verify we're redirected to the student dashboard
    cy.contains('Profilul meu').should('be.visible')
    
    // Verify the correct user info is displayed
    cy.contains('Tudor Albu').should('be.visible')
    
    // Verify student-specific elements exist
    cy.contains('Orarul meu').should('be.visible')
    
    // Log out
    cy.get('button[tooltip="Deconectare"]').click()
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
  })

  it('should login as professor via Google auth', () => {
    // We're going to use a simplified approach to test the Google auth flow
    cy.visit('/auth/login')
    
    // Click the Google sign-in button
    cy.get('#googleSignInButton button').click({ force: true })
    
    // Allow time for any dialogs or transitions
    cy.wait(2000)
    
    // For dev mode, the app should show a user selection dialog
    // We'll try to find and click a professor option if it exists
    cy.get('body').then(($body) => {
      // If there's a selection dialog for test users
      if ($body.find('.user-select-dialog, .test-user-dialog').length > 0) {
        // Find and click on a professor option
        cy.contains('Professor').click({ force: true })
      } else {
        // If no dialog, we're likely in a test environment where we need to manually set the token
        // Use window to set a mock token
        cy.window().then(win => {
          const mockToken = 'professor@usv.ro|CD|null';
          if (win.app && win.app.$store) {
            win.app.$store.dispatch('auth/loginWithGoogle', mockToken);
          } else {
            localStorage.setItem('mockGoogleToken', mockToken);
          }
        })
      }
    })
    
    // Wait for navigation to complete after auth
    cy.url().should('not.include', '/auth/login', { timeout: 15000 })
    
    // Look for navigation elements that should exist after successful login
    cy.get('nav, .sidebar, .navigation-drawer, .v-navigation-drawer', { timeout: 15000 }).should('exist')
    
    // Log out - using more flexible selector
    cy.get('button[tooltip="Deconectare"], .logout-button, button:contains("Logout")', { timeout: 10000 })
      .first().click({ force: true })
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
  })

  it('should login as secretariat via Google auth', () => {
    cy.loginWithGoogle('secretary')
    
    // Verify we're redirected to the secretariat dashboard
    cy.contains('Planificare Examene').should('be.visible')
    
    // Verify the correct user info is displayed
    cy.contains('Alina Berca').should('be.visible')
    
    // Log out
    cy.get('button[tooltip="Deconectare"]').click()
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
  })
})
