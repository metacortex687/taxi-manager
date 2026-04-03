import { renderUploadFileField } from "../render/render-upload-file-field.js"
import { uploadFile } from "../api/fetch-data.js"

const form = {
    entity: "/api/v1/enterprises/",
    fields: [
        {
            render_fn: renderUploadFileField,
            nameGeneratedEvent: "tripArchiveSelected",
            buttonLabel: "Загрузить",
            actionButton: async (file, entity) => {
                if (!file) {
                    allert_message("Выберите файл архива")
                    return
                }

                await uploadFile(
                    `/api/v1/enterprises/${entity.id}/import/trips/${encodeURIComponent(file.name)}/`,
                    file,
                )
            }
        },
    ]
}

window.form = form