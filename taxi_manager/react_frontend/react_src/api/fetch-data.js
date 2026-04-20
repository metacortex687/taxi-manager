// import { clear_massages, allert_message } from "../ui/messages.js";

const authorizationFetch = async (url, options = {}) => {
    const tokenAuth = localStorage.getItem("tokenAuth")

    return await fetch(url, {
        ...options,
        credentials: "omit",
        headers: {
            ...(options.headers || {}),
            "Authorization": `Token ${tokenAuth}`,
        },
    })
}

const fetchDataJSON = async (url, method = "GET", body=undefined, publicData=false) => {
    const requestMethod = publicData ? fetch : authorizationFetch
    // clear_massages()

    const response = await requestMethod(url, {
        method: method,
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        body: body,
    })

    const data = response.status === 204 ? {} : await response.json()

    if (!response.ok) {
        console.log(data)
        if (data.detail === undefined) {  
            // allert_message(JSON.stringify(data))                 
            return data
        }

        // allert_message(data.detail)
        
    } 
    
    return data
} 

const uploadFile = async (url, file, method = "PUT") => {
    // clear_massages()

    const response = await authorizationFetch(url, {
        method: method,
        headers: {
            "Accept": "application/json",
            "Content-Type": file.type || "application/octet-stream",
        },
        body: file,
    })

    // if (!response.ok) {
    //     allert_message(`HTTP ${response.status}`)
    // }

    return response
}

export {fetchDataJSON, uploadFile}