import { fetchDataJSON } from "./fetch-data.js"    

const loadUserInfo = async () => {
    // const tokenAuth = localStorage.getItem("tokenAuth")
    // if (tokenAuth === null) {
    //     return null
    // }
    return await fetchDataJSON("/api/v1/auth/users/me/")
} 

// window.onload = async () => {
//     const tokenAuth = localStorage.getItem("tokenAuth")
//     if (tokenAuth === null && window.location.pathname !== "/login/") {
//         const curent_href = window.location.href;
//         console.log(window.location.pathname)
//         window.location = `${window.location.origin}/login/?next=${curent_href}`
//     };

//     if (window.location.pathname !== "/login/") {
//         await loadUserInfo()
//     }
    
    
//     await window.initPage() //Определено в дочерних шаблонах
// }

const logoutForm = document.getElementById("logoutForm")
if (logoutForm) {
    logoutForm.onsubmit = (e) => {
        e.preventDefault()
        localStorage.removeItem("tokenAuth")
        location.reload()
    } 
}

export {loadUserInfo}