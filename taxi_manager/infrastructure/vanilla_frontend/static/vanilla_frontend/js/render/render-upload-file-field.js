const renderUploadFileField = (field, entity, parentElement) => {
    const wrapper = parentElement

    wrapper.innerHTML = `
        <div class="row g-2 align-items-end">
            <div class="col-md-10">
                <label for="inputUploadFile" class="form-label">Архив</label>
                <input
                    type="file"
                    class="form-control"
                    id="inputUploadFile"
                    accept=".zip"
                >
            </div>

            <div class="col-md-2">
                <button
                    type="button"
                    class="btn btn-primary w-100 js-upload-file-btn"
                >
                    ${field?.buttonLabel || "Загрузить"}
                </button>
            </div>
        </div>
    `

    const inputFile = wrapper.querySelector("#inputUploadFile")
    const buttonUpload = wrapper.querySelector(".js-upload-file-btn")

    buttonUpload.addEventListener("click", () => {
        const detail = {
            file: inputFile.files[0] || null
        }

        window.dispatchEvent(new CustomEvent(field.nameGeneratedEvent, {
            detail
        }))
    })

    if (field?.actionButton) {
        buttonUpload.addEventListener("click", () => {
            const file = inputFile.files[0] || null
            field.actionButton(file, entity)
        })
    }
}

export { renderUploadFileField }