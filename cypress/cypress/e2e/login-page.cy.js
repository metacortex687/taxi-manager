describe('Авторизация', () => {
  const openLoginPage = () => {
    cy.visit('/')
    cy.location('pathname').should('eq', '/login')
  }

  const submitLoginForm = (username, password) => {
    openLoginPage()
    cy.get('#inputUser').type(username)
    cy.get('#inputPassword').type(password)
    cy.get('button[type="submit"]').click()
  }

  it('Сайт доступен', () => {
    openLoginPage()

    cy.get('#inputUser').should('be.visible')
    cy.get('#inputPassword').should('be.visible')
  })

  it('Успешная авторизация', () => {
    submitLoginForm('manager1', 'manager1')

    cy.location('pathname').should('eq', '/')
    cy.get('#usernameLabel').should('have.text', 'manager1')
  })

  it('Неуспешная авторизация', () => {
    submitLoginForm('manager1', 'wrong')

    cy.location('pathname').should('eq', '/login')
    cy.get('#usernameLabel').should('have.text', 'Не авторизован')
  })

  it('Выход из аккаунта', () => {
    submitLoginForm('manager1', 'manager1')

    cy.location('pathname').should('eq', '/')
    cy.get('#usernameLabel').should('have.text', 'manager1')
    cy.get('#logoutForm > button[type="submit"]').click()

    cy.location('pathname').should('eq', '/login')
    cy.get('#usernameLabel').should('have.text', 'Не авторизован')
  })
})
