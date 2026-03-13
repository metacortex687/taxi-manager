import {htmlIdField} from "../entity.js"

const renderInputField = async (field, entity) => {
    const id = htmlIdField(field)
    const value = entity[field["source_name"]] || ""
    const label = field.label

    return `
        <div class="mb-3">
            <label for="${id}" class="form-label">${label}</label>
            <input type="text" class="form-control" id="${id}" value="${value}">
        </div> 
    `
}

const renderInputDateTimeField = async (field, entity) => {
    const id = htmlIdField(field)
    const value = entity[field["source_name"]] || ""
    const label = field.label

    const date = new Date(value) //Создается в ISO/Z

    const local_datetime = new Date(
            date.getTime() - date.getTimezoneOffset() * 60000)
            .toISOString().slice(0, 16)

    return `
        <div class="mb-3">
            <label for="${id}" class="form-label">${label}</label>
            <input type="datetime-local" class="form-control" id="${id}" value="${local_datetime}">
        </div> 
    `
}

const renderSelectedField = async (field, entity) => {
    const id = htmlIdField(field)
    const selected_data = (await fetch_data(field.options.source)).results
    const label = field.label
    const isSelect = (_entity, selected_record) => _entity[field["source_name"]] === selected_record.id
    const representation = field.options.display_name_fn
    const placeholder = field.options.placeholder

    const options = selected_data.map(option_data => `
        <option value="${option_data.id}" ${isSelect(entity, option_data) ? "selected" : ""}>${representation(option_data)}</option>
    `).join("")

    const hasSelectedOption = selected_data.some(option_data => isSelect(entity, option_data))

    return `
        <div class="mb-3">
            <label for="${id}" class="form-label">${label}</label>
            <select class="form-select" id="${id}">
                <option value="" ${hasSelectedOption ? "" : "selected"} disabled>${placeholder}</option>
                ${options}
            </select>
        </div>
    `
}

const renderMultySelectedDriverField = (form_drivers_data) => {

    const lis = form_drivers_data.map(record => `
            <li class="list-group-item d-flex justify-content-between align-items-center js-removed-item">
                <span>${record.last_name} ${record.first_name}</span>
                <button type="button" class="btn btn-sm btn-outline-danger js-btn-remove-item">×</button>
            </li>
    `).join("")



    return `
        <div class="mb-3">
            <label for="inputDrivers" class="form-label">Водители:</label>
            <ul class="list-group" id="inputDrivers">
            ${lis}
            </ul>
        </div>             
    `
}


export { renderInputField, renderSelectedField, renderMultySelectedDriverField, renderInputDateTimeField}
