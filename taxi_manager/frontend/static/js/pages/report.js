import { fetchDataJSON } from "../api/fetch-data.js"

const loadFieldData = async (fieldConfig, data = {}) => {
    const loadedData = { ...data }

    if (fieldConfig.data?.value_data) {
        loadedData.value_data = await fetchDataJSON(fieldConfig.data.value_data)
    }

    return loadedData
}

const renderList = async (parentElement, fieldConfig, data = {}) => {
    const loadedData = await loadFieldData(fieldConfig, data)

    if (fieldConfig.data?.set_form_state) {
        fieldConfig.data.set_form_state(loadedData.value_data, formState)
    }

    for (const field of fieldConfig.field) {
        await field.render(parentElement, field, loadedData)
    }
}

const renderOptionField = async (parentElement, field, data) => {
    const response = await fetchDataJSON(field.data.list_data)
    const items = response.results || response || []

    const wrapper = document.createElement("div")
    wrapper.className = "mb-3"

    const fieldId = `field_${field.formStateField}`
    const selectedValue = formState[field.formStateField] ?? ""

    wrapper.innerHTML = `
        <label for="${fieldId}" class="form-label">${field.label_name}</label>
        <select id="${fieldId}" class="form-select">
            <option value="">${field.placeholder || "Выберите значение"}</option>
            ${items.map(item => `
                <option value="${field.valueFromItem(item)}">
                    ${field.titleFromItem(item)}
                </option>
            `).join("")}
        </select>
    `

    parentElement.appendChild(wrapper)

    const select = wrapper.querySelector("select")
    select.value = selectedValue === null ? "" : String(selectedValue)

    select.onchange = () => {
        const selectedItem = items.find(
            item => String(field.valueFromItem(item)) === select.value
        )

        if (!selectedItem) {
            formState[field.formStateField] = null
            return
        }

        formState[field.formStateField] = field.valueFromItem(selectedItem)

        if (field.onSelect) {
            field.onSelect({ item: selectedItem, field, data })
        }
    }
}

const renderSearchField = async (parentElement, field, data) => {
    const wrapper = document.createElement("div")
    wrapper.className = "mb-3"

    const fieldId = `field_${field.formStateField}`

    wrapper.innerHTML = `
        <label for="${fieldId}" class="form-label">${field.label_name}</label>
        <input
            id="${fieldId}"
            type="text"
            class="form-control"
            placeholder="${field.placeholder || ""}"
            autocomplete="off"
        >
        <div class="list-group mt-1"></div>
    `

    parentElement.appendChild(wrapper)

    const input = wrapper.querySelector("input")
    const list = wrapper.querySelector(".list-group")

    const selectedValue = formState[field.formStateField]

    if (selectedValue !== null) {
        const selectedItem = await fetchDataJSON(
            `${field.data.list_data}${selectedValue}/`
        )

        if (selectedItem) {
            input.value = field.titleFromItem(selectedItem)
        }
    }

    const clearList = () => {
        list.innerHTML = ""
    }

    const renderItems = (items) => {
        clearList()

        for (const item of items) {
            const button = document.createElement("button")
            button.type = "button"
            button.className = "list-group-item list-group-item-action"
            button.textContent = field.titleFromItem(item)

            button.onclick = () => {
                input.value = field.titleFromItem(item)
                formState[field.formStateField] = field.valueFromItem(item)

                if (field.onSelect) {
                    field.onSelect({ item, field, data })
                }

                clearList()
            }

            list.appendChild(button)
        }
    }

    input.oninput = async () => {
        const searchValue = input.value.trim()

        if (!searchValue) {
            formState[field.formStateField] = null
            clearList()
            return
        }

        const queryString = field.search
            ? field.search({ searchValue, formState, field, data })
            : `q=${encodeURIComponent(searchValue)}`

        const url = queryString
            ? `${field.data.list_data}?${queryString}`
            : field.data.list_data

        const response = await fetchDataJSON(url)
        const items = response.results || []

        renderItems(items)
    }
}

const renderBtn = async (parentElement, field, data) => {
    const wrapper = document.createElement("div")
    wrapper.className = "mb-3"

    const button = document.createElement("button")
    button.type = field.type || "button"
    button.className = field.className || "btn btn-primary"
    button.textContent = field.label_name

    button.onclick = () => {
        document.dispatchEvent(new CustomEvent(field.emit_event_name))

        if (field.onClick) {
            field.onClick({ field, data, formState })
        }
    }

    wrapper.appendChild(button)
    parentElement.appendChild(wrapper)
}

const renderEventField = async (parentElement, field, data) => {
    const wrapper = document.createElement("div")
    wrapper.className = "mb-3"

    parentElement.appendChild(wrapper)

    document.addEventListener(field.listen_event_name, async () => {
        if (!field.onEvent) {
            return
        }

        await field.onEvent(wrapper, field, data)
    })
}

const tableReport = async (wrapper, field, data) => {
    const reportType = field.report_type

    const params = field.getParams()

    const createdReport = await fetchDataJSON(
        `/api/v1/reports/${reportType}/`,
        "POST",
        JSON.stringify(params),
    )

    if (!createdReport?.uuid) {
        wrapper.innerHTML = ""
        return
    }

    const reportResponse = await fetchDataJSON(
        `/api/v1/reports/${reportType}/${createdReport.uuid}/`
    )

    const rows = reportResponse.result || []
    const headers = data.value_data?.headers || []

    if (!headers.length) {
        wrapper.innerHTML = `<div class="alert alert-danger">Не удалось получить заголовки отчета</div>`
        return
    }


    if (!rows.length) {
        wrapper.innerHTML = `<div class="alert alert-info">Нет данных для отображения</div>`
        return
    }


    wrapper.innerHTML = `
        <div class="table-responsive">
            <table class="table table-bordered table-striped">
                <thead>
                    <tr>
                        ${headers.map(header => `<th>${header.verbose_name}</th>`).join("")}
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            ${headers.map(header => `<td>${row[header.name] ?? ""}</td>`).join("")}
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `

}


const formState = {
    enterprise: null,
    vehicle: null,
    frequency: null,
    period_from: null,
    period_to: null,
}

const form = {
    render: renderList,
    field: [
        {
            render: renderList,
            data: {
                value_data: "/api/v1/reports/carmileagereport/",
                set_form_state: (valueData, formState) => {

                        const values = valueData["params"] || {}

                        const fields = ["enterprise", "vehicle", "frequency", "period_from", "period_to"]

                        for (const fieldName of fields) {
                            if (fieldName in values) {
                                formState[fieldName] = values[fieldName]
                            }
                        }

                    },
            },
            field: [
                {
                    name: "enterprise",
                    label_name: "Предприятие",
                    placeholder: "Выберите предприятие",
                    data: {
                        list_data: "/api/v1/enterprises/",
                    },
                    render: renderOptionField,
                    formStateField: "enterprise",
                    valueFromItem: (item) => item.id,
                    titleFromItem: (item) => item.name,
                    onSelect: () => {
                        formState.vehicle = null
                    },
                },
                {
                    name: "vehicle",
                    label_name: "Автомобиль",
                    placeholder: "Начните вводить номер или модель",
                    data: {
                        list_data: "/api/v1/vehicles/",
                    },
                    render: renderSearchField,
                    formStateField: "vehicle",
                    valueFromItem: (item) => item.id,
                    titleFromItem: (item) => item.display_name,
                    search: ({ searchValue, formState }) => {
                        const params = new URLSearchParams()

                        if (searchValue) {
                            params.set("q", searchValue)
                        }

                        params.set("enterprise", formState.enterprise)

                        return params.toString()
                    },
                },
                 {
                    name: "frequency",
                    label_name: "Период",
                    placeholder: "Выберите период",
                    data: {
                        list_data: "/api/v1/reports/frequencies/",
                    },
                    render: renderOptionField,
                    formStateField: "frequency",
                    valueFromItem: (item) => item.id,
                    titleFromItem: (item) => item.display_name,
                },               
                {
                    name: "build_report_btn",
                    label_name: "Сформировать отчет",
                    render: renderBtn,
                    emit_event_name: "build_report",
                    className: "btn btn-primary",
                },
                {
                    name: "report_result",
                    render: renderEventField,
                    listen_event_name: "build_report",
                    report_type: "carmileagereport",
                    getParams: () => ({
                        enterprise: formState.enterprise,
                        vehicle: formState.vehicle,
                        frequency: formState.frequency,
                        period_from: "2026-03-01T00:00:00+00:00",
                        period_to: "2026-03-31T23:59:59+00:00",
                    }),
                    onEvent: tableReport,

                },
            ]
        },
    ]
}

window.initPage = async () => {
    const formHTMLElement = document.getElementById("form_fields")
    await form.render(formHTMLElement, form, {})
    window.formState = formState
}