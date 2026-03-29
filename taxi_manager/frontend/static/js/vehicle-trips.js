import { renderMapField } from "./api/render-map.js";

const form = {
        // entity: "/api/v1/vehicles/<int:pk>/trip-points/?from=2026-03-01T00:00:00%2B03:00&to=2026-03-31T23:59:59%2B03:00&offset=41",
        // entity: "/api/v1/vehicles/<int:pk>/locations/?response_format=geojson",   
        entity: "/api/v1/vehicles/<int:pk>/trip-points/?from=2026-03-01T00:00:00%2B03:00&to=2026-03-31T23:59:59%2B03:00&&response_format=geojson",    
        fields: [
            {
                source_name: "list",
                empty_value: [],
                updateEvent: "tripSelected",
                render_fn: renderMapField,  
             },
        ]
    }


window.form = form