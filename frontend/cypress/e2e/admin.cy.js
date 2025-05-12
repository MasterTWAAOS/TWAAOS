/// <reference types="cypress" />

describe('Admin Features', () => {
  beforeEach(() => {
    // Login as admin before each test
    cy.loginAsAdmin()
    
    // Verify we're on the admin dashboard
    cy.contains('Dashboard').should('be.visible')
  })

  it('should sync data from USV API', () => {
    // Navigate to the dashboard if not already there
    cy.contains('Dashboard').click()
    
    // Find and click the sync button
    cy.contains('button', 'Sincronizare').click()
    
    // Verify the sync started notification appears
    cy.contains('Sincronizarea datelor a început').should('be.visible')
    
    // Wait for the sync to complete (this may take some time)
    // Set a longer timeout for this step since sync can take time
    cy.contains('Datele au fost sincronizate cu succes', { timeout: 30000 }).should('be.visible')
    
    // Verify the sync status indicator shows success
    cy.get('[data-cy="sync-status"]').should('exist')
  })

  it('should display system statistics', () => {
    // Check that statistics are displayed on the dashboard
    cy.get('[data-cy="stats-card"]').should('exist')
    cy.contains('Grupuri').should('be.visible')
    cy.contains('Utilizatori').should('be.visible')
    cy.contains('Săli').should('be.visible')
    
    // The numbers should be non-zero after a successful sync
    cy.get('[data-cy="stats-card"]').find('.stat-value').each(($el) => {
      cy.wrap($el).invoke('text').then(parseFloat).should('be.gt', 0)
    })
  })

  it('should allow creating a backup', () => {
    // Open the backup dialog
    cy.contains('button', 'Backup').click()
    
    // Dialog should be visible
    cy.get('.backup-dialog').should('be.visible')
    
    // Fill in backup details
    cy.get('[data-cy="backup-name"]').clear().type('test_backup')
    cy.get('[data-cy="include-db"]').check()
    cy.get('[data-cy="include-files"]').check()
    
    // Create the backup
    cy.contains('button', 'Creează Backup').click()
    
    // Verify success message
    cy.contains('Backup-ul a fost creat cu succes').should('be.visible')
  })

  it('should log out successfully', () => {
    // Click logout button
    cy.get('button[tooltip="Deconectare"]').click()
    
    // Verify we're back on the login page
    cy.url().should('include', '/auth/login')
    cy.contains('Autentificare').should('be.visible')
  })
})
