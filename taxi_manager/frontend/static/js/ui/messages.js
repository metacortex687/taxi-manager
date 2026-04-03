const clear_massages = () => {
    const elemMessages = document.getElementById("messages")
    elemMessages.innerHTML = `

    `

}
const allert_message = (text) => {
    const elemMessages = document.getElementById("messages")
    elemMessages.innerHTML = `
    <div class="alert alert-danger" role="alert">
        <div id="messageText"><div>
    </div>
    `

    elemMessages.querySelector("#messageText").textContent = text

}

export {clear_massages, allert_message}