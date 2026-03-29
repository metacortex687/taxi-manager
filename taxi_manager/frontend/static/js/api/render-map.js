import { createDefaultWrapper } from "./render.js"

const renderMapField = (field, entity, parentElement, eventData = {id: undefined}) => {

    console.log(entity)

    const wrapper = parentElement

    // wrapper.style.cssText = field.cssText
    wrapper.style.cssText = "width: 800px; height: 500px;"




    var map = L.map(wrapper, { attributionControl: false });

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // L.marker([51.5, -0.09]).addTo(map)
    //     .bindPopup('A pretty CSS popup.<br> Easily customizable.')
    //     .openPopup();

    const grayIcon = L.icon({
        iconUrl: "/frontend/static/img/marker-gray.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-gray"
    })

    const greenIcon = L.icon({
        iconUrl: "/frontend/static/img/marker-green.png", 
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: "marker-green"
    })

    const geoLayer = L.geoJSON(entity.results, {
        pointToLayer: function (feature, latlng) {

            if (eventData && feature.properties.trip === eventData.id) {
                return L.marker(latlng, { icon:  greenIcon})
            }

            return L.marker(latlng, { icon:  grayIcon})
            
        }
    }).addTo(map);

    const bounds = geoLayer.getBounds()
    map.fitBounds(bounds)

}


export { renderMapField }