/// <reference types="cypress" />

describe('Student Features', () => {
  beforeEach(() => {
    // Login as student before each test
    cy.loginWithGoogle('student')
    
    // Wait for app to be fully loaded after login
    cy.wait(3000)
    
    // Verify we're on the student dashboard - more flexible assertions
    cy.get('.v-app-bar', { timeout: 15000 }).should('be.visible')
    cy.get('.v-navigation-drawer', { timeout: 15000 }).should('be.visible')
  })

  it('should display schedule properly', () => {
    // Navigate to schedule page
    cy.contains('Orarul meu', { timeout: 10000 }).click({ force: true })
    
    // Verify schedule components are present
    cy.get('.fc-view-harness').should('be.visible')  // FullCalendar component
    cy.get('.fc-toolbar-title').should('be.visible') // Calendar title
    
    // Verify that the group name is displayed (should be "Test FIESC Group")
    cy.contains('Test FIESC Group').should('be.visible')
  })

  it('should show exam schedule', () => {
    // Navigate to exam schedule page
    cy.contains('Examene').click()
    
    // Verify exam list or calendar is displayed
    cy.get('.exam-schedule').should('be.visible')
    cy.contains('Sesiune').should('be.visible')
  })

  it('should allow viewing profile information', () => {
    // Navigate to profile page
    cy.contains('Profilul meu').click()
    
    // Verify profile information is displayed
    cy.contains('Tudor Albu').should('be.visible')
    cy.contains('student1@student.usv.ro').should('be.visible')
    cy.contains('Student').should('be.visible')
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
