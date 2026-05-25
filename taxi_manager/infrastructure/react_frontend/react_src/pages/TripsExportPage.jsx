import { Link, useParams } from "react-router-dom"
import { useState } from "react"

import { fetchDataJSON } from "../api/fetch-data"

import routes from "../routes"

import { useQuery } from "@tanstack/react-query"
import { DatePickerInput } from "@mantine/dates"

import toast from 'react-hot-toast'

function TripsExportPage() {
    const { enterprise_id } = useParams()
    const [period, setPeriod] = useState([null, null])

    const handleExport = () => {
        const [dateFrom, dateTo] = period

        if (!dateFrom || !dateTo) {
            toast.error("Период выбран не полностью")
            return
        }

        toast.success("Скачивание началось")
        window.location.href = routes.trips.export.api(enterprise_id,dateFrom,dateTo)
    }





    return (
        <div>
            <h1>Экспорт за период</h1>

            <div className="mb-3">
                <DatePickerInput
                    type="range"
                    label="Период"
                    placeholder="Выберите период"
                    value={period}
                    onChange={setPeriod}
                    clearable
                />
            </div>

            <button
                type="button"
                className="btn btn-primary"
                onClick={handleExport}
            >
                Скачать
            </button>
        </div>
    )

}


export default TripsExportPage