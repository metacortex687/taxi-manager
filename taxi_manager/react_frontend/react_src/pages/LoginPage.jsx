
import React from "react"
import AuthContext from "../auth/AuthContest"
import { Navigate } from "react-router-dom"

class LoginPage extends React.Component {
  static contextType = AuthContext


  constructor(props) {
    super(props)

    this.state = {userName: null, password: null}
  }

  handleChangeUserName = (e) => {
    e.preventDefault()
    this.setState({userName: e.target.value})
  }

  handleChangePassword = (e) => {
    e.preventDefault()
    this.setState({password: e.target.value})
  }

  handleSubmit= async (e) => {
    e.preventDefault()
    const result = await this.context.loginUser(this.state.userName, this.state.password)

  }

  render() {

    if (this.context.isAuthenticated === true) {
      return <Navigate to="/" />
    }

    return (
      <form className="d-flex justify-content-center" id="authForm" onSubmit={this.handleSubmit}>
        <div className="auth-box mb-3">
            <h1 className="text-center">Авторизуйтесь</h1>
            <div className="mb-3">
                <label htmlFor="inputUser" className="form-label">Пользователь:</label>
                <input type="text" className="form-control" id="inputUser" onChange={this.handleChangeUserName}/>
            </div>
            <div className="mb-3">
                <label htmlFor="inputPassword" className="form-label">Пароль:</label>
                <input type="password" className="form-control" id="inputPassword" onChange={this.handleChangePassword}/>
            </div>  
            <button type="submit" className="btn btn-primary">Войти</button>
        </div>
      </form>
    )
  }
}

export default LoginPage