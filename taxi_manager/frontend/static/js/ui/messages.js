const clear_massages = () => {
    const elemMessages = document.getElementById("messages")
    elemMessages.innerHTML = `

    `

}

const render_message = (text, type) => {
    const elemMessages = document.getElementById("messages")
    elemMessages.innerHTML = `
        <div class="alert alert-${type}" role="alert">
            <div id="messageText"></div>
        </div>
    `

    elemMessages.querySelector("#messageText").textContent = text
}


const allert_message = (text) => {
    render_message(text, "danger")
}

const success_message = (text) => {
    render_message(text, "success")
}

export {clear_massages, allert_message, success_message}