import { createDefaultWrapper } from "../render/render.js"

const renderMapField = (field, entity, parentElement, eventData = { id: undefined }) => {

    console.log(entity)

    const wrapper = createDefaultWrapper(parentElement)


    // wrapper.style.cssText = field.cssText
    wrapper.style.cssText = "width: 800px; height: 500px;"

    var map = L.map(wrapper, { attributionControl: false });

    // Отрисовка линий маршрутов
    // {


    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);


    const geoLayer = L.geoJSON(entity.results).addTo(map);
    // }

    // Отрисовка стартовых точек маршрута
    // {
    const grayIconEnd = L.icon({
        iconUrl: "/vanilla_frontend/static/img/marker-gray-start.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-gray"
    })

    const greenIconEnd = L.icon({
        iconUrl: "/vanilla_frontend/static/img/marker-green-start.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-green"
    })

    let start_points = []
    entity.results.features.forEach(
        (feature) => {
            if (feature.geometry.type === "LineString") {
                start_points.push(
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: feature.geometry.coordinates[0],
                        },
                        properties: {
                            trip: feature.properties.trip
                        }
                    }
                )

            }

        }
    )
    const geoJSONstartPoints = {
        type: 'FeatureCollection',
        features: start_points

    }

    L.geoJSON(geoJSONstartPoints
        ,
        {
            pointToLayer: function (feature, latlng) {

                if (eventData && feature.properties.trip === eventData.id) {
                    return L.marker(latlng, { icon: greenIconEnd })
                }

                return L.marker(latlng, { icon: grayIconEnd })

            }
        }).addTo(map);
    // }

    // Отрисовка конечных точек маршрута
    // {
    const grayIconStart = L.icon({
        iconUrl: "/vanilla_frontend/static/img/marker-gray-end.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-gray"
    })

    const greenIconStart = L.icon({
        iconUrl: "/vanilla_frontend/static/img/marker-green-end.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-green"
    })

    let end_points = []
    entity.results.features.forEach(
        (feature) => {
            if (feature.geometry.type === "LineString") {
                end_points.push(
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: feature.geometry.coordinates[feature.geometry.coordinates.length - 1],
                        },
                        properties: {
                            trip: feature.properties.trip
                        }
                    }
                )

            }

        }
    )
    const geoJSONendPoints = {
        type: 'FeatureCollection',
        features: end_points

    }
    console.log(geoJSONendPoints)
    L.geoJSON(geoJSONendPoints
        ,
        {
            pointToLayer: function (feature, latlng) {

                if (eventData && feature.properties.trip === eventData.id) {
                    return L.marker(latlng, { icon: greenIconStart })
                }

                return L.marker(latlng, { icon: grayIconStart })

            }
        }).addTo(map);
    // } 

    //Позиционирование карты
    // {
    const bounds = geoLayer.getBounds()
    if (bounds.isValid()) {
        map.fitBounds(bounds)
        return
    }
    map.setView([61, 105], 3)
    // }

}


export { renderMapField }