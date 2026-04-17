import { renderUploadFileField } from "../render/render-upload-file-field.js"
import { uploadFile } from "../api/fetch-data.js"
import { clear_massages, allert_message, success_message } from "../ui/messages.js"

const form = {
    entity: "/api/v1/enterprises/",
    fields: [
        {
            render_fn: renderUploadFileField,
            nameGeneratedEvent: "tripArchiveSelected",
            buttonLabel: "Загрузить",
            actionButton: async (file, entity) => {
                clear_massages()

                if (!file) {
                    allert_message("Выберите файл архива")
                    return
                }

                success_message(`Начало загрузки "${file.name}" `)

                try {
                    await uploadFile(
                        `/api/v1/enterprises/${entity.id}/import/trips/${encodeURIComponent(file.name)}/`,
                        file,
                    )

                    success_message(`Файл "${file.name}" успешно загружен`)
                } catch (error) {
                    allert_message("Не удалось загрузить файл")
                }
            }
        },
    ]
}

window.form = form