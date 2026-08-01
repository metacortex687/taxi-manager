describe('Предприятия', () => {
  const openLoginPage = () => {
    cy.visit('/')
    cy.location('pathname').should('eq', '/login')
  }

  const submitLoginForm = (username, password) => {
    openLoginPage()
    cy.get('#inputUser').type(username)
    cy.get('#inputPassword').type(password)
    cy.get('button[type="submit"]').click()
    cy.location('pathname').should('eq', '/')
  }

  it('Список предприятий не пуст', () => {
    submitLoginForm('manager1', 'manager1')    

    cy.visit('/enterprises') 
    
    cy.get('table tbody tr')
    .should('have.length.greaterThan', 0)

  })

})