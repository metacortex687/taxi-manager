import { Link } from "react-router-dom"
import AuthContext from "../auth/AuthContest"

import urls from "../urls"

import React from "react"

class TopNavbar extends React.Component {    
    static contextType = AuthContext

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
                        <Link to={urls.index()} className="btn btn-secondary btn-lg rounded-1 btn-light border  d-inline-flex align-items-center" style={{ height: "48px" }}><i className="fa fa-home icon-border"></i></Link>
                    </li>
                    <li className="nav-item">
                        <Link to={urls.enterprises()} className="btn btn-secondary btn-lg rounded-1 btn-light border">Предприятия</Link>
                    </li>
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