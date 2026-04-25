import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"

import toast from "react-hot-toast"

import FormInput from "../components/FormInput"
import FormSelect from "../components/FormSelect"
import FormInputDate from "../components/FormInputDate"

const EMPTY_FORM = {
    enterprise: "",
    model: "",
    number: "",
    mileage: "",
    price: "",
    vin: "",
    year_of_manufacture: "",
    purchased_at: "",
}



function VehicleEditPage() {
    const { vehicle_id } = useParams()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const [formData, setFormData] = useState(EMPTY_FORM)
    const [isInitialized, setIsInitialized] = useState(false)

    const vehicleQuery = useQuery({
        queryKey: ["vehicle", vehicle_id],
        queryFn: async () => await fetchDataJSON(routes.vehicleEdit.api(vehicle_id)),
    })

    const enterprisesQuery = useQuery({
        queryKey: ["enterprises"],
        queryFn: async () => (await fetchDataJSON(routes.enterprises.api())).results,
    })

    const modelsQuery = useQuery({
        queryKey: ["models"],
        queryFn: async () => (await fetchDataJSON("/api/v1/models/")).results,
    })

    useEffect(() => {
        if (!vehicleQuery.data || isInitialized) {
            return
        }

        setFormData({
            enterprise: vehicleQuery.data.enterprise_id,
            model: vehicleQuery.data.model_id,
            number: vehicleQuery.data.number || "",
            mileage: vehicleQuery.data.mileage || "",
            price: vehicleQuery.data.price || "",
            vin: vehicleQuery.data.vin || "",
            year_of_manufacture: vehicleQuery.data.year_of_manufacture || "",
            purchased_at: vehicleQuery.data.purchased_at || "",
        })
        setIsInitialized(true)
    }, [vehicleQuery.data, isInitialized])

    const prepareVehicleSaveData = (formData) => ({
        enterprise_id: formData.enterprise,
        model_id: formData.model,
        number: formData.number,
        mileage: formData.mileage,
        price: formData.price,
        vin: formData.vin,
        year_of_manufacture: formData.year_of_manufacture,
        purchased_at: formData.purchased_at,
    })

    const updateVehicleMutation = useMutation({
        mutationFn: async (entity) =>
            await fetchDataJSON(
                routes.vehicleEdit.api(vehicle_id),
                "PUT",
                JSON.stringify(prepareVehicleSaveData(entity)),
            ),
        onSuccess: async () => {
            toast.success("Автомобиль сохранен")
            await queryClient.invalidateQueries({ queryKey: ["vehicle", vehicle_id] })
            await queryClient.invalidateQueries({ queryKey: ["vehicles"] })
        },
        onError: (error) => {
            toast.error(error.message || "Не удалось сохранить автомобиль")
        },
    })

    const deleteVehicleMutation = useMutation({
        mutationFn: async () =>
            await fetchDataJSON(routes.vehicleEdit.api(vehicle_id), "DELETE"),
        onSuccess: async () => {
            toast.success("Автомобиль удален")
            await queryClient.invalidateQueries({ queryKey: ["vehicles"] })
            navigate(routes.enterprises.url())
        },
        onError: (error) => {
            toast.error(error.message || "Не удалось удалить автомобиль")
        },
    })

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData((current) => ({
            ...current,
            [name]: value,
        }))
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        updateVehicleMutation.mutate(formData)
    }

    const handleDelete = () => {
        const isConfirmed = window.confirm("Удалить автомобиль?")

        if (!isConfirmed) {
            return
        }

        deleteVehicleMutation.mutate()
    }

    if (
        vehicleQuery.isPending ||
        enterprisesQuery.isPending ||
        modelsQuery.isPending
    ) {
        return <p>Загрузка...</p>
    }

    if (vehicleQuery.isError) {
        return <p>Ошибка: {vehicleQuery.error.message}</p>
    }

    if (enterprisesQuery.isError) {
        return <p>Ошибка: {enterprisesQuery.error.message}</p>
    }

    if (modelsQuery.isError) {
        return <p>Ошибка: {modelsQuery.error.message}</p>
    }

    const isLoading =
        updateVehicleMutation.isPending || deleteVehicleMutation.isPending

    return (
        <form onSubmit={handleSubmit}>
            <h1>Редактирование автомобиля</h1>

            <Link to={routes.trips.url(vehicle_id)}>{routes.trips.link_name}</Link>

            <FormSelect
                id="vehicle_enterprise"
                name="enterprise"
                label="Предприятие:"
                value={formData.enterprise}
                onChange={handleChange}
                placeholder="Выберите предприятие"
                items={enterprisesQuery.data}
                getOptionLabel={(enterprise) => `${enterprise.name} (${enterprise.city})`}
            />

            <FormSelect
                id="vehicle_model"
                name="model"
                label="Бренд:"
                value={formData.model}
                onChange={handleChange}
                placeholder="Выберите бренд"
                items={modelsQuery.data}
                getOptionLabel={(model) => model.name}
            />

            <FormInput
                id="vehicle_number"
                name="number"
                label="Номер:"
                value={formData.number}
                onChange={handleChange}
            />

            <FormInput
                id="vehicle_mileage"
                name="mileage"
                label="Пробег (км):"
                value={formData.mileage}
                onChange={handleChange}
            />

            <FormInput
                id="vehicle_price"
                name="price"
                label="Цена (руб):"
                value={formData.price}
                onChange={handleChange}
            />

            <FormInput
                id="vehicle_vin"
                name="vin"
                label="VIN:"
                value={formData.vin}
                onChange={handleChange}
            />

            <FormInput
                id="vehicle_year_of_manufacture"
                name="year_of_manufacture"
                label="Год выпуска:"
                value={formData.year_of_manufacture}
                onChange={handleChange}
            />

            <FormInputDate
                id="vehicle_purchased_at"
                name="purchased_at"
                label="Приобретено:"
                value={formData.purchased_at}
                onChange={handleChange}
            />

            <div className="d-flex gap-2">
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isLoading}
                >
                    {updateVehicleMutation.isPending ? "Сохранение..." : "Сохранить"}
                </button>

                <button
                    type="button"
                    className="btn btn-danger"
                    onClick={handleDelete}
                    disabled={isLoading}
                >
                    {deleteVehicleMutation.isPending ? "Удаление..." : "Удалить"}
                </button>
            </div>
            
        </form>
    )
}

export default VehicleEditPage