import AuthContext from "../auth/AuthContest"

import React from "react"
import { Navigate, Outlet } from "react-router-dom"

class RequireAuth extends React.Component {  
    static contextType = AuthContext

    constructor(props) {
        super(props)
    }

    render() {
        if(this.context.isAuthenticated === null) {
            return null
        }

        if(this.context.isAuthenticated === false){
            return <Navigate to="/login" />
        }

        return <Outlet/>
    }

}

export default RequireAuth