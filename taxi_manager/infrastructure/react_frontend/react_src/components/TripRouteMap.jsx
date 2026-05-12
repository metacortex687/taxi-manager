import { useEffect, useMemo, useRef } from "react"
import L from "leaflet"
import { GeoJSON, MapContainer, Marker, TileLayer, useMap } from "react-leaflet"
import "leaflet/dist/leaflet.css"

const markerGrayStartUrl = "/static/react_frontend/img/marker-gray-start.png"
const markerGreenStartUrl = "/static/react_frontend/img/marker-green-start.png"
const markerGrayEndUrl = "/static/react_frontend/img/marker-gray-end.png"
const markerGreenEndUrl = "/static/react_frontend/img/marker-green-end.png"

const DEFAULT_CENTER = [61, 105]
const DEFAULT_ZOOM = 3

const createMarkerIcon = (iconUrl) =>
  L.icon({
    iconUrl,
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  })

const markerIcons = {
  grayStart: createMarkerIcon(markerGrayStartUrl),
  greenStart: createMarkerIcon(markerGreenStartUrl),
  grayEnd: createMarkerIcon(markerGrayEndUrl),
  greenEnd: createMarkerIcon(markerGreenEndUrl),
}

const toLatLng = ([lng, lat]) => [lat, lng]

const getRoutePoint = (feature, pointType) => {
  const coordinates = feature.geometry.coordinates
  const pointCoordinates =
    pointType === "start" ? coordinates[0] : coordinates[coordinates.length - 1]

  return {
    trip: feature.properties.trip,
    position: toLatLng(pointCoordinates),
  }
}

function FitBounds({ geoJson }) {
  const map = useMap()

  useEffect(() => {
    const layer = L.geoJSON(geoJson)
    const bounds = layer.getBounds()

    if (bounds.isValid()) {
      map.fitBounds(bounds)
      return
    }

    map.setView(DEFAULT_CENTER, DEFAULT_ZOOM)
  }, [map, geoJson])

  return null
}

function RoutesGeoJsonLayer({ geoJson }) {
  const layerKeyRef = useRef(0)
  const previousGeoJsonRef = useRef(geoJson)

  if (previousGeoJsonRef.current !== geoJson) {
    previousGeoJsonRef.current = geoJson
    layerKeyRef.current += 1
  }

  return <GeoJSON key={layerKeyRef.current} data={geoJson} />
}

function TripRouteMap({ routeGeoJson, selectedTripId }) {
  const routeFeatures = useMemo(
    () =>
      routeGeoJson.features.filter(
        (feature) => feature.geometry.type === "LineString"
      ),
    [routeGeoJson]
  )

  const startPoints = useMemo(
    () => routeFeatures.map((feature) => getRoutePoint(feature, "start")),
    [routeFeatures]
  )

  const endPoints = useMemo(
    () => routeFeatures.map((feature) => getRoutePoint(feature, "end")),
    [routeFeatures]
  )

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      attributionControl={false}
      style={{ width: "800px", height: "500px" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <RoutesGeoJsonLayer geoJson={routeGeoJson} />
      <FitBounds geoJson={routeGeoJson} />

      {startPoints.map((point) => (
        <Marker
          key={`start-${selectedTripId}-${point.trip}`}
          position={point.position}
          icon={
            point.trip === selectedTripId
              ? markerIcons.greenStart
              : markerIcons.grayStart
          }
        />
      ))}

      {endPoints.map((point) => (
        <Marker
          key={`end-${selectedTripId}-${point.trip}`}
          position={point.position}
          icon={
            point.trip === selectedTripId
              ? markerIcons.greenEnd
              : markerIcons.grayEnd
          }
        />
      ))}
    </MapContainer>
  )
}

export default TripRouteMap