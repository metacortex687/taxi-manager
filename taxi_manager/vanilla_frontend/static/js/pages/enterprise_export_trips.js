import { renderMapField } from "../render/render-map.js";
import { renderListTripField } from "../render/render-list-trip.js";
import { renderPeriodField } from "../render/render-period-field.js";

const form = {
    // entity: "/api/v1/vehicles/<int:pk>/trip-points/?from=2026-03-01T00:00:00%2B03:00&to=2026-03-31T23:59:59%2B03:00&offset=41",
    // entity: "/api/v1/vehicles/<int:pk>/locations/?response_format=geojson",   
    entity: "/api/v1/enterprises/",
    fields: [
        {
            render_fn: renderPeriodField,
            nameGeneratedEvent: "periodSelected",
            buuttonLable: "Скачать",
            actionButton: (from, to, entity,) => {
                window.location.href = `/api/v1/enterprises/${entity.id}/export/trips/?from=${from}&to=${to}` //Не закрыто токеном
            }
        },
    ]
}


window.form = form