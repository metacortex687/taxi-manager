import {loadUserInfo, logout, loginUser} from "../api/users.js"
import AuthContext from "./AuthContest";

import React from "react"

class AuthProvider extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            userInfo: null,
            isAuthenticated: null
        }
    }

    async componentDidMount() {
        const token = localStorage.getItem("tokenAuth")

        if (!token) {
            this.setState({
                userInfo: null,
                isAuthenticated: false,
            })
            return
        }

        await this.login(token)

    }

    login = async () => {
        const userInfo = await loadUserInfo()

        const isAuthenticated = userInfo?.username ? true : false

        this.setState(
            {
                userInfo,                
                isAuthenticated,
            }
        )        
    }

    loginUser = async (username, password) => {
        await loginUser(username, password)
        this.login()
    }   

    logout = () => {
        logout()
        this.setState({
                userInfo: null,
                isAuthenticated: false
            })
    }

    render() {
        const value = {
            isAuthenticated: this.state.isAuthenticated,
            userInfo: this.state.userInfo,
            // login: this.login,
            logout: this.logout,
            loginUser: this.loginUser
        } 

        return (
            <AuthContext.Provider value={value}>
                {this.props.children}
            </AuthContext.Provider>
        )
    }

}

export default AuthProvider