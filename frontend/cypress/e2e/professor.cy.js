/// <reference types="cypress" />

describe('Professor Features', () => {
  beforeEach(() => {
    // Login as professor before each test
    cy.loginWithGoogle('professor')
    
    // Wait for app to be fully loaded after login
    cy.wait(3000)
    
    // Verify we're on the dashboard - looking for navigation elements instead of specific text
    cy.get('.v-app-bar', { timeout: 15000 }).should('be.visible')
    cy.get('.v-navigation-drawer', { timeout: 15000 }).should('be.visible')
  })

  it('should display schedule properly', () => {
    // Navigate to schedule page
    cy.contains('Orarul meu', { timeout: 10000 }).click({ force: true })
    
    // Verify schedule components are present
    cy.get('.fc-view-harness').should('be.visible')  // FullCalendar component
    cy.get('.fc-toolbar-title').should('be.visible') // Calendar title
  })

  it('should allow setting availability preferences', () => {
    // Navigate to availability page
    cy.contains('Disponibilitate').click()
    
    // Verify availability form elements are present
    cy.get('.availability-form').should('be.visible')
    
    // Test selecting availability preferences
    cy.get('[data-cy="day-select"]').click()
    cy.contains('Luni').click()
    
    cy.get('[data-cy="start-time"]').type('09:00')
    cy.get('[data-cy="end-time"]').type('12:00')
    
    cy.get('[data-cy="add-availability"]').click()
    
    // Verify availability is added to the list
    cy.contains('Luni, 09:00 - 12:00').should('be.visible')
  })

  it('should display assigned exams', () => {
    // Navigate to exams page
    cy.contains('Examene').click()
    
    // Verify exam list components are visible
    cy.get('.exam-list').should('be.visible')
    
    // Professor should see what exams they are assigned to
    cy.contains('Sesiune').should('be.visible')
    cy.contains('Disciplina').should('be.visible')
    cy.contains('Grupa').should('be.visible')
  })

  it('should allow viewing profile information', () => {
    // Navigate to profile page
    cy.contains('Profilul meu').click()
    
    // Verify profile information is displayed
    cy.contains('Matei Neagu').should('be.visible')
    cy.contains('professor@fiesc.usv.ro').should('be.visible')
    cy.contains('Professor').should('be.visible')
    cy.contains('Departament: C').should('be.visible')
  })

  it('should log out successfully', () => {
    // Click logout button
    cy.get('button[tooltip="Deconectare"]').click()
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
    cy.contains('Autentificare').should('be.visible')
  })
})
