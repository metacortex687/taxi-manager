import { createDefaultWrapper } from "./render.js"

const renderMapField = (field, entity, parentElement) => {

    console.log(entity)

    const wrapper = createDefaultWrapper(parentElement)

    // wrapper.style.cssText = field.cssText
    wrapper.style.cssText = "width: 800px; height: 500px;"




    var map = L.map(wrapper, { attributionControl: false }).setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // L.marker([51.5, -0.09]).addTo(map)
    //     .bindPopup('A pretty CSS popup.<br> Easily customizable.')
    //     .openPopup();

    const lineLayer = L.geoJSON(entity.results, {
        style: function (feature) {
            return { color: '#1976d2', weight: 4, opacity: 0.9 };
        }
    }).addTo(map);

}


export { renderMapField }