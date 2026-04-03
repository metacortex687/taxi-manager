import { clear_massages } from "../ui/messages.js";

const authorizationFetch = async (url, options = {}) => {
    const tokenAuth = localStorage.getItem("tokenAuth")

    return await fetch(url, {
        ...options,
        headers: {
            ...(options.headers || {}),
            "Authorization": `Token ${tokenAuth}`,
        },
    })
}

const fetchDataJSON = async (url, method = "GET", body=undefined) => {
    const tokenAuth = localStorage.getItem("tokenAuth")

    clear_massages()

    const response = await fetch(url, {
        method: method,
        headers: { "Accept": "application/json", "Content-Type": "application/json", "Authorization": `Token ${tokenAuth}` },
        body: body
    })

    const data = response.statusText === "No Content" ? {} : await response.json()

    if (!response.ok) {
        console.log(data)
        if (data.detail === undefined) {  
            allert_message(JSON.stringify(data))                 
            return data
        }

        allert_message(data.detail)
        
    } 
    
    return data
} 

export {fetchDataJSON}