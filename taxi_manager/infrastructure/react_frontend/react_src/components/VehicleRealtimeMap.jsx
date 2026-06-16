import { useEffect, useState } from "react"
import L from "leaflet"
import { MapContainer, Marker, Polyline, TileLayer, useMap } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import routes from "../routes"

const markerVehicleUrl = "/static/react_frontend/img/marker-green-end.png"

const DEFAULT_CENTER = [55.5159391, 37.3020111]
const DEFAULT_ZOOM = 15

const vehicleMarkerIcon = L.icon({
  iconUrl: markerVehicleUrl,
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

function MoveMapToPosition({ position }) {
  const map = useMap()

  useEffect(() => {
    if (position) {
      map.setView(position, DEFAULT_ZOOM)
    }
  }, [map, position])

  return null
}

function VehicleRealtimePath({ vehicleId }) {
  const [points, setPoints] = useState([])

  useEffect(() => {
    setPoints([])

    const eventSource = new EventSource(
      routes.vehicleTracking.api(vehicleId)
    )

    eventSource.onmessage = (event) => {
      const point = JSON.parse(event.data)

      setPoints((previousPoints) => [
        ...previousPoints,
        [point.lat, point.lng],
      ])
    }

    eventSource.onerror = (error) => {
      console.error("SSE error", error)
    }

    return () => {
      eventSource.close()
    }
  }, [vehicleId])

  const currentPosition = points[points.length - 1]

  return (
    <>
      <MoveMapToPosition position={currentPosition} />

      {points.length > 1 && (
        <Polyline positions={points} />
      )}

      {currentPosition && (
        <Marker
          position={currentPosition}
          icon={vehicleMarkerIcon}
        />
      )}
    </>
  )
}

function VehicleRealtimeMap({ vehicleId }) {
  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      attributionControl={false}
      style={{ width: "800px", height: "500px" }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <VehicleRealtimePath vehicleId={vehicleId} />
    </MapContainer>
  )
}

export default VehicleRealtimeMap