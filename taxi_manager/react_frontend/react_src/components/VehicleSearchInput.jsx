import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"
import FormInput from "./FormInput"

function VehicleSearchInput({ enterpriseId, vehicleId, onChange }) {
    const [searchValue, setSearchValue] = useState("")
    const [title, setTitle] = useState("")

    const vehicleSearchQuery = useQuery({
        queryKey: ["vehicles-search", enterpriseId, searchValue],
        queryFn: async () =>
            (await fetchDataJSON(routes.vehicles.searchApi(enterpriseId, searchValue))).results,
        enabled: Boolean(enterpriseId && searchValue),
    })

    const selectedVehicleQuery = useQuery({
        queryKey: ["vehicle", vehicleId],
        queryFn: () => fetchDataJSON(routes.vehicleEdit.api(vehicleId)),
        enabled: Boolean(vehicleId),
    })

    useEffect(() => {
        setSearchValue("")
        setTitle("")
    }, [enterpriseId])

    useEffect(() => {
        if (!selectedVehicleQuery.data) {
            return
        }

        setTitle(selectedVehicleQuery.data.display_name)
    }, [selectedVehicleQuery.data])

    const handleChange = (event) => {
        const value = event.target.value

        setTitle(value)
        setSearchValue(value)
        onChange(null)
    }

    const handleSelect = (vehicle) => {
        setTitle(vehicle.display_name)
        setSearchValue("")
        onChange(vehicle.id)
    }

    const vehicles = searchValue ? vehicleSearchQuery.data || [] : []

    return (
        <div className="mb-3">
            <FormInput
                id="vehicle"
                name="vehicle"
                label="Автомобиль:"
                placeholder={enterpriseId ? "Начните вводить номер или модель" : "Сначала выберите предприятие"}
                value={title}
                onChange={handleChange}
                disabled={!enterpriseId}
                autoComplete="off"
            />

            {vehicleSearchQuery.isError && (
                <div className="text-danger mt-1">
                    Ошибка подбора автомобиля: {vehicleSearchQuery.error.message}
                </div>
            )}

            {vehicles.length > 0 && (
                <div className="list-group mt-1">
                    {vehicles.map((vehicle) => (
                        <button
                            key={vehicle.id}
                            type="button"
                            className="list-group-item list-group-item-action"
                            onClick={() => handleSelect(vehicle)}
                        >
                            {vehicle.display_name}
                        </button>
                    ))}
                </div>
            )}
        </div>
    )
}

export default VehicleSearchInput