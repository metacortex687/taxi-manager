import { renderInputField } from "./api/render.js";

const form = {
        entity: "/api/v1/enterprises/",
        fields: [
            {
                source_name: "name",
                empty_value: undefined,
                label: "Наименование:",
                render_fn: renderInputField
            },
            {
                source_name: "city",
                empty_value: undefined,
                label: "Город:",
                render_fn: renderInputField
            },
        ]
    }

window.form = form
