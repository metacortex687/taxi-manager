import {loadUserInfo, logout} from "../api/users.js"
import AuthContext from "../auth/AuthContest"

import React from "react"

class TopNavbar extends React.Component {    
    static contextType = AuthContext

    async componentDidMount() {
        const userInfo = await loadUserInfo()
        this.setState({ userInfo })
    }

    handleSubmitLogout = (e) => {
        e.preventDefault()
        this.context.logout()
    }



    render() {
        const {isAuthenticated, userInfo} = this.context

        const nameUser =  userInfo?.username || "Не авторизован"

        return (
            <nav className="navbar navbar-expand-lg navbar-light bg-light px-3" >
                <ul className="navbar-nav d-flex flex-row align-items-center w-100">
                    <li className="nav-item">
                        <a href="#" className="btn btn-secondary btn-lg rounded-1 btn-light border">
                            Отчеты
                        </a>
                    </li>
                    <li className="nav-item ms-auto">
                        <form id="logoutForm" onSubmit={this.handleSubmitLogout}>
                            <label htmlFor="usernameLabel">Пользователь:</label>
                            <label id="usernameLabel">{nameUser}</label>
                            {isAuthenticated ?  <button type="submit" >Выйти</button> : null}    
                        </form>                        
                    </li>                    
                </ul>
            </nav>
        )
    }
}

export default TopNavbar