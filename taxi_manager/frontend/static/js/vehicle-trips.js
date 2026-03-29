import { renderMapField } from "./api/render-map.js";
import { renderListTripField } from "./api/render-list-trip.js";
import { renderPeriodField } from "./api/render-period-field.js";

const form = {
        // entity: "/api/v1/vehicles/<int:pk>/trip-points/?from=2026-03-01T00:00:00%2B03:00&to=2026-03-31T23:59:59%2B03:00&offset=41",
        // entity: "/api/v1/vehicles/<int:pk>/locations/?response_format=geojson",   
  
        fields: [
            {
                entity: "/api/v1/vehicles/<int:pk>/trip-points/?response_format=geojson",  
                source_name: "list",
                empty_value: [],
                updateViewEvent: "tripSelected",
                updateDataEvent: "periodSelected",
                render_fn: renderMapField,  
             },
            {
                render_fn: renderPeriodField,
            },            
            {
                entity: "/api/v1/vehicles/<int:pk>/trips/",  
                empty_value: [],
                render_fn: renderListTripField,  
             },
        ]
    }


window.form = form