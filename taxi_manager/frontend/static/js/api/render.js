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
    const idHtml = htmlIdField(field)
    const items = (await fetch_data(field.options.source)).results
    const placeholderText = field.options.placeholder

    const displayName = (item) => field.options.display_name_fn(item)
    
    const isSelect = (item) => entity[field["source_name"]] === item.id
    const hasSelectedOption = () => items.some(item => isSelect(item))

    const renderPlaceholderOption = (_) => `<option value="" ${hasSelectedOption() ? "" : "selected"} disabled>${placeholderText}</option>`
    const renderOption = (item) => `<option value="${item.id}" ${isSelect(item) ? "selected" : ""}>${displayName(item)}</option>`

    const renderOptions = () => 
        [renderPlaceholderOption(), ...items.map(renderOption)]
        .join("")

    return `
        <div class="mb-3">
            <label for="${idHtml}" class="form-label">${field.label}</label>
            <select class="form-select" id="${idHtml}">                
                ${renderOptions()}
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
