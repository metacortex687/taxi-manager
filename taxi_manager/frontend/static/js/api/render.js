import {htmlIdField} from "../entity.js"
import {fromISOtoLocaleDateTime} from "./date-time.js"

const createElementFromHTML = (html) => {
    const template = document.createElement("template")
    template.innerHTML = html.trim()
    return template.content.firstElementChild
}

const createDefaultWrapper = (parentElement) => {
    const wrapper = createElementFromHTML(`
        <div class="mb-3"></div>
    `)
    parentElement.appendChild(wrapper)
    return wrapper
}

const renderInputField = async (field, entity, parentElement) => {
    const id = htmlIdField(field)
    const value = entity[field["source_name"]] || ""
    const label = field.label

    const wrapper = parentElement
    wrapper.innerHTML =`
            <label for="${id}" class="form-label">${label}</label>
            <input type="text" class="form-control" id="${id}" value="${value}">
    `
}

const renderInputDateTimeField = async (field, entity, parentElement) => {
    const id = htmlIdField(field)
    const value = entity[field["source_name"]] || ""
    const label = field.label

    let local_datetime = fromISOtoLocaleDateTime(value)

    const wrapper = parentElement
    wrapper.innerHTML =`
            <label for="${id}" class="form-label">${label}</label>
            <input type="datetime-local" class="form-control" id="${id}" value="${local_datetime}">
    `
}

const renderSelectedField = async (field, entity, parentElement) => {
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

    const wrapper = parentElement
    wrapper.innerHTML =`
            <label for="${idHtml}" class="form-label">${field.label}</label>
            <select class="form-select" id="${idHtml}">                
                ${renderOptions()}
            </select>
    `
}

const renderMultySelectedDriverField = (form_drivers_data, parentElement) => {

    const lis = form_drivers_data.map(record => `
            <li class="list-group-item d-flex justify-content-between align-items-center js-removed-item">
                <span>${record.last_name} ${record.first_name}</span>
                <button type="button" class="btn btn-sm btn-outline-danger js-btn-remove-item">×</button>
            </li>
    `).join("")


    const wrapper = parentElement
    wrapper.innerHTML = `
            <label for="inputDrivers" class="form-label">Водители:</label>
            <ul class="list-group" id="inputDrivers">
            ${lis}
            </ul>      
    `
}


export { renderInputField, renderSelectedField, renderMultySelectedDriverField, renderInputDateTimeField, createDefaultWrapper}
