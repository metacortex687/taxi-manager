import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"

import toast from "react-hot-toast"

const EMPTY_FORM = {
    name: "",
    city: "",
    time_zone: "",
}

function EnterpriseEditPage() {
    const { enterprise_id } = useParams()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const [formData, setFormData] = useState(EMPTY_FORM)
    const [isInitialized, setIsInitialized] = useState(false)

    const enterpriseQuery = useQuery({
        queryKey: ["enterprise", enterprise_id],
        queryFn: async () => await fetchDataJSON(routes.enterpriseEdit.api(enterprise_id)),
    })

    const timeZonesQuery = useQuery({
        queryKey: ["timezones"],
        queryFn: async () => (await fetchDataJSON("/api/v1/timezones/")).results,
    })

    useEffect(() => {
        if (!enterpriseQuery.data || isInitialized) {
            return
        }

        console.log(enterpriseQuery.data)
        setFormData({
            name: enterpriseQuery.data.name,
            city: enterpriseQuery.data.city,
            time_zone: enterpriseQuery.data.time_zone,
        })
        setIsInitialized(true)
    }, [enterpriseQuery.data, isInitialized])

    const updateEnterpriseMutation = useMutation({
        mutationFn: async (entity) =>
            await fetchDataJSON(
                routes.enterpriseEdit.api(enterprise_id),
                "PUT",
                JSON.stringify(entity),
            ),
        onSuccess: async () => {
            toast.success("Предприятие сохранено")
            await queryClient.invalidateQueries({ queryKey: ["enterprise", enterprise_id] })
            await queryClient.invalidateQueries({ queryKey: ["enterprises"] })
        },
        onError: (error) => {
            toast.error(error.message || "Не удалось сохранить предприятие")
        },
    })

    const deleteEnterpriseMutation = useMutation({
        mutationFn: async () =>
            await fetchDataJSON(routes.enterpriseEdit.api(enterprise_id), "DELETE"),
        onSuccess: async () => {
            toast.success("Предприятие удалено")
            await queryClient.invalidateQueries({ queryKey: ["enterprises"] })
            navigate(routes.enterprises.url())
        },
        onError: (error) => {
            toast.error(error.message || "Не удалось удалить предприятие")
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
        updateEnterpriseMutation.mutate(formData)
    }

    const handleDelete = () => {
        const isConfirmed = window.confirm("Удалить предприятие?")

        if (!isConfirmed) {
            return
        }

        deleteEnterpriseMutation.mutate()
    }

    if (enterpriseQuery.isPending || timeZonesQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (enterpriseQuery.isError) {
        return <p>Ошибка: {enterpriseQuery.error.message}</p>
    }

    if (timeZonesQuery.isError) {
        return <p>Ошибка: {timeZonesQuery.error.message}</p>
    }

    const isLoading =
        updateEnterpriseMutation.isPending || deleteEnterpriseMutation.isPending

    return (
        <form onSubmit={handleSubmit}>
            <h1>Редактирование предприятия</h1>

            <div className="mb-3">
                <label htmlFor="enterprise_name" className="form-label">
                    Наименование:
                </label>
                <input
                    id="enterprise_name"
                    name="name"
                    type="text"
                    className="form-control"
                    value={formData.name}
                    onChange={handleChange}
                />
            </div>

            <div className="mb-3">
                <label htmlFor="enterprise_city" className="form-label">
                    Город:
                </label>
                <input
                    id="enterprise_city"
                    name="city"
                    type="text"
                    className="form-control"
                    value={formData.city}
                    onChange={handleChange}
                />
            </div>

            <div className="mb-3">
                <label htmlFor="enterprise_time_zone" className="form-label">
                    Временная зона:
                </label>
                <select
                    id="enterprise_time_zone"
                    name="time_zone"
                    className="form-select"
                    value={formData.time_zone}
                    onChange={handleChange}
                >
                    <option value="">Выберите временную зону</option>
                    {timeZonesQuery.data.map((timeZone) => (
                        <option key={timeZone.id} value={timeZone.id}>
                            {timeZone.display_name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="d-flex gap-2">
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isLoading}
                >
                    {updateEnterpriseMutation.isPending ? "Сохранение..." : "Сохранить"}
                </button>

                <button
                    type="button"
                    className="btn btn-danger"
                    onClick={handleDelete}
                    disabled={isLoading}
                >
                    {deleteEnterpriseMutation.isPending ? "Удаление..." : "Удалить"}
                </button>
            </div>
        </form>
    )
}

export default EnterpriseEditPage