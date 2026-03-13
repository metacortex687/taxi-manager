import { renderInputField, renderSelectedField } from "./api/render.js";


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
            {
                source_name: "time_zone",
                empty_value: undefined,
                label: "Временная зона:",
                options : {
                    source: "/api/v1/timezones/",
                    placeholder: "Выберите временную зону",
                    display_name_fn: (option_entity) => option_entity.display_name,
                }

            },
        ]
    }

window.form = form
