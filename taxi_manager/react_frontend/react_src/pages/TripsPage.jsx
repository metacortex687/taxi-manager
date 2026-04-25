import dayjs from "dayjs"
import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useParams } from "react-router-dom"
import { Button, Table } from "react-bootstrap"
import { DatePickerInput } from "@mantine/dates"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"
import TripRouteMap from "../components/TripRouteMap"

const EMPTY_FEATURE_COLLECTION = {
    type: "FeatureCollection",
    features: [],
}

function TripsPage() {
    const { vehicle_id } = useParams()
    const [period, setPeriod] = useState([null, null])
    const [appliedPeriod, setAppliedPeriod] = useState([null, null])
    const [selectedTripId, setSelectedTripId] = useState()

    const [dateFrom, dateTo] = appliedPeriod

    const tripPointsQuery = useQuery({
        queryKey: ["vehicle-trip-points", vehicle_id, dateFrom, dateTo],
        queryFn: async () =>
            (await fetchDataJSON(routes.trips.api.points(vehicle_id, dateFrom, dateTo))).results,
    })

    const tripsQuery = useQuery({
        queryKey: ["vehicle-trips", vehicle_id, dateFrom, dateTo],
        queryFn: async () =>
            (await fetchDataJSON(routes.trips.api.list(vehicle_id, dateFrom, dateTo))).results,
    })

    const handlePeriodChange = (value) => {
        setPeriod(value)
    }

    const handlePeriodApply = () => {
        setSelectedTripId()
        setAppliedPeriod(period)
    }

    if (tripPointsQuery.isPending || tripsQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (tripPointsQuery.isError) {
        return <p>Ошибка загрузки карты: {tripPointsQuery.error.message}</p>
    }

    if (tripsQuery.isError) {
        return <p>Ошибка загрузки поездок: {tripsQuery.error.message}</p>
    }

    const routeGeoJson = tripPointsQuery.data ?? EMPTY_FEATURE_COLLECTION
    const trips = tripsQuery.data ?? []

    return (
        <div>
            <h1 className="text-center">Маршруты</h1>

            <TripRouteMap
                routeGeoJson={routeGeoJson}
                selectedTripId={selectedTripId}
            />

            <div className="mb-3 mt-3">
                <DatePickerInput
                    type="range"
                    label="Период"
                    placeholder="Выберите период"
                    value={period}
                    onChange={handlePeriodChange}
                    clearable
                    popoverProps={{ zIndex: 3000 }}
                />
            </div>

            <div className="mb-3">
                <Button type="button" onClick={handlePeriodApply}>
                    Применить
                </Button>
            </div>

            <Table hover className="mt-3">
                <thead>
                    <tr>
                        <th scope="col">ID</th>
                        <th scope="col">Время начала</th>
                        <th scope="col">Адрес начала</th>
                        <th scope="col">Время окончания</th>
                        <th scope="col">Адрес окончания</th>
                    </tr>
                </thead>
                <tbody>
                    {trips.map((trip) => (
                        <tr
                            key={trip.id}
                            onClick={() => setSelectedTripId(trip.id)}
                            className={trip.id === selectedTripId ? "table-active" : ""}
                            style={{ cursor: "pointer" }}
                        >
                            <td>{trip.id}</td>
                            <td>{dayjs(trip.started_at).format("YYYY.MM.DD HH:mm")}</td>
                            <td>{trip.start_point.address}</td>
                            <td>{dayjs(trip.ended_at).format("YYYY.MM.DD HH:mm")}</td>
                            <td>{trip.end_point.address}</td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    )
}

export default TripsPage