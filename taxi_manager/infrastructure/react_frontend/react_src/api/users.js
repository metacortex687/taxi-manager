import { data } from "react-router-dom"
import { fetchDataJSON } from "./fetch-data.js"    

const loadUserInfo = async () => {
    return await fetchDataJSON("/api/v1/auth/users/me/")
} 

const logout = () => {
    localStorage.removeItem("tokenAuth")
}

const loginUser = async (username, password) => {
    const data = await fetchDataJSON(
        "/api/v1/auth/token/login/",
        "POST",
        JSON.stringify({
            username: username,
            password: password,
        }),
        true
    )

    localStorage.setItem("tokenAuth", data.auth_token)     
}

export {loadUserInfo, logout, loginUser}