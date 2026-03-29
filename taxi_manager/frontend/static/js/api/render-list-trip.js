import { createDefaultWrapper } from "./render.js"
import {fromISOtoLocaleDateTimeString} from "./date-time.js"

const renderListTripField = (field, entity, parentElement) => {
    const trips = entity.results || []

    const rows = trips.map(record => `
        <tr class="js-trip-row" data-id="${record.id}" style="cursor: pointer;">
            <td>${record.id}</td>
            <td>${fromISOtoLocaleDateTimeString(record.started_at)}</td>
            <td>${record.start_point.address}</td>
            <td>${fromISOtoLocaleDateTimeString(record.ended_at)}</td>
            <td>${record.end_point.address}</td>
        </tr>
    `).join("")

    const wrapper = parentElement
    wrapper.innerHTML = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Время начала</th>
                        <th>Адрес начала</th>
                        <th>Время окончания</th>
                        <th>Адрес окончания</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
    `

    const tbody = wrapper.querySelector("tbody")

    tbody.addEventListener("click", (event) => {
        const row = event.target.closest(".js-trip-row")
        if (!row) {
            return
        }

        tbody.querySelectorAll(".js-trip-row").forEach(element => {
            element.classList.remove("table-active")
        })

        row.classList.add("table-active")

        window.dispatchEvent(new CustomEvent("tripSelected", {
            detail: {
                id: Number(row.dataset.id)
            }
        }))
    })
}

export { renderListTripField }