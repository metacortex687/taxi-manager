import TripRouteMap from "./TripRouteMap"

const toFeatureCollection = (path) => ({
    type: "FeatureCollection",
    features: path.map((item, index) => {
        if (item.type === "Feature") {
            return {
                ...item,
                properties: {
                    ...item.properties,
                    trip: item.properties?.trip ?? index,
                },
            }
        }

        return {
            type: "Feature",
            geometry: item,
            properties: {
                trip: index,
            },
        }
    }),
})

function CarRoutesReportRow({ row, headers, timeZone }) {
    const formatCellValue = (header) => {
        const value = row[header.name]

        if (header.name === "date" && value) {
            return new Intl.DateTimeFormat("ru-RU", {
                timeZone,
                dateStyle: "short",
            }).format(new Date(value))
        }

        return value ?? ""
    }

    const renderCellValue = (header) => {
        const value = row[header.name]

        if (header.name === "path") {
            if (!Array.isArray(value) || value.length === 0) {
                return ""
            }

            return (
                <TripRouteMap
                    routeGeoJson={toFeatureCollection(value)}
                    selectedTripId={undefined}
                />
            )
        }

        return formatCellValue(header)
    }

    return (
        <tr>
            {headers.map((header) => (
                <td key={header.name}>
                    {renderCellValue(header)}
                </td>
            ))}
        </tr>
    )
}

export default CarRoutesReportRow