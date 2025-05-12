/// <reference types="cypress" />

describe('Secretariat Features', () => {
  beforeEach(() => {
    // Login as secretariat before each test
    cy.loginWithGoogle('secretary')
    
    // Verify we're on the secretariat dashboard
    cy.contains('Planificare', { timeout: 10000 }).should('be.visible')
    // Allow more flexible name matching
    cy.get('.user-info').should('be.visible', { timeout: 10000 })
  })

  it('should display the exam planning interface', () => {
    // Navigate to exam planning page
    cy.contains('Planificare Examene').click()
    
    // Verify planning components are visible
    cy.get('.planning-interface').should('be.visible')
    cy.contains('Sesiune').should('be.visible')
    cy.contains('Generare Program').should('be.visible')
  })

  it('should allow creating a new exam session', () => {
    // Navigate to sessions page
    cy.contains('Sesiuni').click()
    
    // Click button to create new session
    cy.contains('Sesiune Nouă').click()
    
    // Fill in session details
    cy.get('[data-cy="session-name"]').type('Sesiune de Vară 2025')
    cy.get('[data-cy="start-date"]').type('2025-06-15')
    cy.get('[data-cy="end-date"]').type('2025-06-30')
    
    // Save the session
    cy.contains('Salvează').click()
    
    // Verify success message
    cy.contains('Sesiunea a fost creată cu succes').should('be.visible')
    
    // Verify new session appears in the list
    cy.contains('Sesiune de Vară 2025').should('be.visible')
  })

  it('should allow managing rooms', () => {
    // Navigate to rooms page
    cy.contains('Săli').click()
    
    // Verify room list is displayed
    cy.get('.room-list').should('be.visible')
    
    // View room details
    cy.contains('tr', 'C1').find('button[icon="pi pi-eye"]').click()
    
    // Verify room details dialog opens
    cy.get('.room-details-dialog').should('be.visible')
    cy.contains('Capacitate').should('be.visible')
  })

  it('should allow managing groups', () => {
    // Navigate to groups page
    cy.contains('Grupe').click()
    
    // Verify group list is displayed
    cy.get('.group-list').should('be.visible')
    
    // Check that test group exists
    cy.contains('Test FIESC Group').should('be.visible')
  })

  it('should log out successfully', () => {
    // Click logout button
    cy.get('button[tooltip="Deconectare"]').click()
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
    cy.contains('Autentificare').should('be.visible')
  })
})
