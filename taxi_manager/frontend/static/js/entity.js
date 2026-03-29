import { createDefaultWrapper } from "./api/render.js"

const convertSnakeToCamelCase = (str) => {
        return str
            .split("_")
            .map((word, index) => 
                index === 0 
                    ? word 
                    : word.charAt(0).toUpperCase() + word.slice(1))
            .join("")
    }

export const htmlIdField = (formField) => convertSnakeToCamelCase(`${formField.type}_${formField.source_name}`)

const authForm = document.getElementById("authForm")

// authForm.onsubmit = async (event) => {
// };



const getAction = () => {
    return document.getElementById("pageData").dataset.action
}

const getPk = () => {
    return document.getElementById("pageData").dataset.pkEntity
}

const isNew = () => {
    return getAction() === "new"
}

const emptyEntity = () => {
    res = {}
    for(let field of form.fields) {
        res[field.source_name] = field.empty_value    
    }

    return res
}

const loadEntity = async () => {

    const patch = form.entity.includes("<int:pk>") ? form.entity.replace("<int:pk>",getPk()) : `${form.entity}${getPk()}/`

    return await fetch_data(patch)
}

const renderFormField = async (entity, field, formHTMLElement) => {
    const wrapper = createDefaultWrapper(formHTMLElement)

    const render = async (eventData = null) => {
        wrapper.innerHTML = ""
        await field.render_fn(field, entity, wrapper, eventData)
    }

    await render()

    if (field.updateEvent) {
        window.addEventListener(field.updateEvent, async (event) => {
            await render(event.detail)
        })
    }

}

const renderForm = async () => {

    const formHTMLElement = document.getElementById("form_fields")

    const entity = isNew() ? emptyEntity() : await loadEntity()

    for (const field of form.fields) {
        await renderFormField(entity, field, formHTMLElement)
    }

    // form_drivers_data = (await fetch_data(`/api/v1/drivers/?id__in=${form_data.driver_ids.join(",")}&ordering=last_name,first_name`)).results //Водителей пока не рредактирую
    // form_fields.innerHTML += renderMultySelectedDriverField(form_drivers_data)
}



const deleteEntity = async () => {
    const pkVehicle = document.getElementById("pageData").dataset.pkVehicle
    // const result = await fetch_data(`/api/v1/vehicles/${pkVehicle}/`, method = "DELETE")
    const result = await fetch_data(`${form.entity}${getPk()}/`,  method = "DELETE")
    window.location.href = "/enterprises/"
}

const updateEntity = async (entity) => {
    const result = await fetch_data(`${form.entity}${getPk()}/`, "PUT", JSON.stringify(entity))
}

const saveNewEntity = async (entity) => {
    // const result = await fetch_data(`/api/v1/vehicles/`, "POST", JSON.stringify(entity))
    const result = await fetch_data(`${form.entity}${getPk()}/`, "POST", JSON.stringify(entity))
    window.location.href = `/vehicles/${result.id}/edit/`
}

const entityFromForm = () => {

    let res = {}
    for(let field of form.fields) {
        res[field.source_name] = document.getElementById(htmlIdField(field)).value    
    }

    console.log(res)

    return res
}

const presaveEntity = (entity) => {
    let res = {}
    for(let field of form.fields){
        const presave_fn = field.presave_fn || (value => value)
        res[field.source_name] = presave_fn(entity[field.source_name])
    }
    return res
}

const saveEntity = async () => {

    const entity = presaveEntity(entityFromForm())

    if (isNew()) {
        await saveNewEntity(entity)
        return
    }

    await updateEntity(entity)

}

const initPage = async () => {
    renderForm()

}
window.initPage = initPage


document.addEventListener("click", (event) => {
    const target = event.target
    if (target.classList.contains("js-btn-remove-item")) {
        const item = target.closest(".js-removed-item");
        item.remove()
        return
    }

    if (!target.hasAttribute("data-action")) {
        return
    }

    const action = target.dataset.action

    if (action === "delete") {
        deleteEntity()
        return
    }

    if (action === "save") {
        saveEntity()
        return
    }


})


