import { renderInputField, renderSelectedField, renderInputDateTimeField } from "../render/render.js";

import { convert_from_locale_to_iso } from "../utils/date-time.js"


const form = {
    entity: "/api/v1/vehicles/",
    fields: [
        {
            source_name: "enterprise_id",
            empty_value: undefined,
            label: "Предприятие:",
            render_fn: renderSelectedField,
            options: {
                source: "/api/v1/enterprises/",
                placeholder: "Выберите предприятие",
                display_name_fn: (option_entity) => `${option_entity.name} (${option_entity.city})`
            },
        },
        {
            source_name: "model_id",
            empty_value: undefined,
            label: "Бренд:",
            render_fn: renderSelectedField,
            options: {
                source: "/api/v1/models/",
                placeholder: "Выберите бренд",
                display_name_fn: (option_entity) => option_entity.name
            },
        },
        {
            source_name: "number",
            empty_value: undefined,
            label: "Номер:",
            render_fn: renderInputField,
        },
        {
            source_name: "mileage",
            empty_value: undefined,
            label: "Пробег (км):",
            render_fn: renderInputField,
        },
        {
            source_name: "price",
            empty_value: undefined,
            label: "Цена (руб):",
            render_fn: renderInputField,
        },
        {
            source_name: "vin",
            empty_value: undefined,
            label: "VIN:",
            render_fn: renderInputField,
        },
        {
            source_name: "year_of_manufacture",
            label: "Год выпуска:",
            empty_value: undefined,
            render_fn: renderInputField,
        },
        {
            source_name: "purchased_at",
            label: "Приобретено:",
            empty_value: undefined,
            render_fn: renderInputDateTimeField,
            presave_fn: convert_from_locale_to_iso
        },
    ]
}


window.form = form