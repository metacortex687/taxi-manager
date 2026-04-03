import {convert_from_locale_to_iso} from "./date-time.js"

const renderPeriodField = (field, entity, parentElement) => {
    const wrapper = parentElement

    wrapper.innerHTML = `
        <div class="row g-2 align-items-end">
            <div class="col-md-5">
                <label for="inputPeriodFrom" class="form-label">Начало</label>
                <input
                    type="datetime-local"
                    class="form-control"
                    id="inputPeriodFrom"
                >
            </div>

            <div class="col-md-5">
                <label for="inputPeriodTo" class="form-label">Окончание</label>
                <input
                    type="datetime-local"
                    class="form-control"
                    id="inputPeriodTo"
                >
            </div>

            <div class="col-md-2">
                <button
                    type="button"
                    class="btn btn-primary w-100 js-period-apply-btn"
                >
                    ${field?.buuttonLable || "Применить"}
                </button>
            </div>
        </div>
    `

    const inputFrom = wrapper.querySelector("#inputPeriodFrom")
    const inputTo = wrapper.querySelector("#inputPeriodTo")
    const buttonApply = wrapper.querySelector(".js-period-apply-btn")

    buttonApply.addEventListener("click", () => {
        const detail = {}

        if (inputFrom.value) {
            detail.from = convert_from_locale_to_iso(inputFrom.value)
        }

        if (inputTo.value) {
            detail.to = convert_from_locale_to_iso(inputTo.value)
        }

        window.dispatchEvent(new CustomEvent(field.nameGeneratedEvent, {
            detail
        }))
    })

    if(field?.actionButton) {
        buttonApply.addEventListener("click",() => field?.actionButton(convert_from_locale_to_iso(inputFrom.value), convert_from_locale_to_iso(inputTo.value), entity))
    }
}

export { renderPeriodField }