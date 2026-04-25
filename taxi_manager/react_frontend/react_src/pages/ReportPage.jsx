import dayjs from "dayjs"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Button, Table } from "react-bootstrap"
import { DatePickerInput } from "@mantine/dates"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"
import FormSelect from "../components/FormSelect"
import VehicleSearchInput from "../components/VehicleSearchInput"

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const getDateFromISO = (value) => {
    const datePart = value.slice(0, 10)
    const [year, month, day] = datePart.split("-").map(Number)

    return new Date(year, month - 1, day)
}

const getTimeZoneOffsetMinutes = (date, timeZone) => {
    const parts = new Intl.DateTimeFormat("en-US", {
        timeZone,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hourCycle: "h23",
    }).formatToParts(date)

    const values = Object.fromEntries(
        parts
            .filter(part => part.type !== "literal")
            .map(part => [part.type, Number(part.value)])
    )

    const timeZoneDate = Date.UTC(
        values.year,
        values.month - 1,
        values.day,
        values.hour,
        values.minute,
        values.second
    )

    return (timeZoneDate - date.getTime()) / 60_000
}

const formatOffset = (offsetMinutes) => {
    const sign = offsetMinutes >= 0 ? "+" : "-"
    const absOffset = Math.abs(offsetMinutes)
    const hours = String(Math.floor(absOffset / 60)).padStart(2, "0")
    const minutes = String(absOffset % 60).padStart(2, "0")

    return `${sign}${hours}:${minutes}`
}

const addTimeZoneToDate = (value, timeZone, addDays = 0) => {
    const date = dayjs(value).startOf("day").add(addDays, "day")
    const dateTime = date.format("YYYY-MM-DDT00:00:00")
    const offsetDate = new Date(`${date.format("YYYY-MM-DD")}T00:00:00Z`)
    const offsetMinutes = getTimeZoneOffsetMinutes(offsetDate, timeZone)

    return `${dateTime}${formatOffset(offsetMinutes)}`
}

function ReportPage() {
    const { report_type } = useParams()

    const [formData, setFormData] = useState({
        enterprise: null,
        vehicle: null,
        frequency: null,
        time_zone: null,
    })
    const [period, setPeriod] = useState([null, null])
    const [rows, setRows] = useState([])
    const [statusText, setStatusText] = useState("")
    const [errorText, setErrorText] = useState("")
    const [uuid, setUuid] = useState(null)
    const [canRenderPdf, setCanRenderPdf] = useState(false)
    const [isBuilding, setIsBuilding] = useState(false)

    const reportQuery = useQuery({
        queryKey: ["report-config", report_type],
        queryFn: () => fetchDataJSON(routes.report.api(report_type)),
        enabled: report_type === "carmileagereport",
    })

    const enterprisesQuery = useQuery({
        queryKey: ["enterprises"],
        queryFn: async () => (await fetchDataJSON(routes.enterprises.api())).results,
        enabled: report_type === "carmileagereport",
    })

    const frequenciesQuery = useQuery({
        queryKey: ["report-frequencies"],
        queryFn: async () => {
            const data = await fetchDataJSON(routes.reportFrequencies.api())
            return data.results || data
        },
        enabled: report_type === "carmileagereport",
    })

    useEffect(() => {
        const params = reportQuery.data?.params

        if (!params) {
            return
        }

        setFormData({
            enterprise: params.enterprise,
            vehicle: params.vehicle,
            frequency: params.frequency,
            time_zone: params.time_zone,
        })

        setPeriod([
            params.period_from ? getDateFromISO(params.period_from) : null,
            params.period_to ? getDateFromISO(params.period_to) : null,
        ])
    }, [reportQuery.data])

    if (report_type !== "carmileagereport") {
        return <div className="alert alert-danger">Неизвестный тип отчета</div>
    }

    if (reportQuery.isPending || enterprisesQuery.isPending || frequenciesQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (reportQuery.isError) {
        return <p>Ошибка загрузки отчета: {reportQuery.error.message}</p>
    }

    if (enterprisesQuery.isError) {
        return <p>Ошибка загрузки предприятий: {enterprisesQuery.error.message}</p>
    }

    if (frequenciesQuery.isError) {
        return <p>Ошибка загрузки периодичности: {frequenciesQuery.error.message}</p>
    }

    const headers = reportQuery.data?.headers || []
    const enterprises = enterprisesQuery.data || []
    const frequencies = frequenciesQuery.data || []

    const handleEnterpriseChange = (event) => {
        if (!event.target.value) {
            setFormData({
                ...formData,
                enterprise: null,
                vehicle: null,
                time_zone: null,
            })
            return
        }

        const enterpriseId = Number(event.target.value)
        const enterprise = enterprises.find(item => item.id === enterpriseId)

        setFormData({
            ...formData,
            enterprise: enterpriseId,
            vehicle: null,
            time_zone: enterprise.time_zone_code,
        })
    }

    const formatCellValue = (header, row) => {
        const value = row[header.name]

        if (header.name === "date" && value) {
            return new Intl.DateTimeFormat("ru-RU", {
                timeZone: formData.time_zone,
                dateStyle: "short",
            }).format(new Date(value))
        }

        if (header.name === "mileage" && value !== null && value !== undefined && value !== "") {
            return Number(value).toFixed(1)
        }

        return value ?? ""
    }

    const handleBuildReport = async (event) => {
        event.preventDefault()

        setRows([])
        setUuid(null)
        setCanRenderPdf(false)
        setErrorText("")
        setStatusText("В очереди")
        setIsBuilding(true)

        const [periodFrom, periodTo] = period

        const params = {
            enterprise: formData.enterprise,
            vehicle: formData.vehicle,
            frequency: formData.frequency,
            period_from: addTimeZoneToDate(periodFrom, formData.time_zone),
            period_to: addTimeZoneToDate(periodTo, formData.time_zone, 1),
            time_zone: formData.time_zone,
        }

        try {
            const createdReport = await fetchDataJSON(
                routes.report.api(report_type),
                "POST",
                JSON.stringify(params)
            )

            setUuid(createdReport.uuid)
            setCanRenderPdf(createdReport.can_render_pdf)

            while (true) {
                await wait(300)

                const reportResponse = await fetchDataJSON(
                    routes.report.resultApi(report_type, createdReport.uuid)
                )

                if (reportResponse.status === "PENDING") {
                    setStatusText("В очереди")
                    continue
                }

                if (reportResponse.status === "PROCESSING") {
                    setStatusText("Формируется")
                    continue
                }

                if (reportResponse.status !== "DONE") {
                    setStatusText("")
                    setErrorText("Неизвестный статус задачи")
                    break
                }

                setStatusText("")
                setRows(reportResponse.result || [])
                break
            }
        } catch (error) {
            setStatusText("")
            setErrorText(error.message)
        } finally {
            setIsBuilding(false)
        }
    }

    return (
        <div>
            <h1 className="text-center">Отчет</h1>

            <form onSubmit={handleBuildReport}>
                <div className="mb-3">
                    <DatePickerInput
                        type="range"
                        label="Период отчета"
                        placeholder="Выберите период"
                        value={period}
                        onChange={setPeriod}
                        clearable
                        popoverProps={{ zIndex: 3000 }}
                    />
                </div>

                <FormSelect
                    id="enterprise"
                    name="enterprise"
                    label="Предприятие:"
                    value={formData.enterprise ?? ""}
                    onChange={handleEnterpriseChange}
                    placeholder="Выберите предприятие"
                    items={enterprises}
                    getOptionLabel={(enterprise) => enterprise.name}
                />

                <div className="mb-3">
                    <label className="form-label">Временная зона:</label>
                    <div className="form-control-plaintext">
                        {formData.time_zone}
                    </div>
                </div>

                <VehicleSearchInput
                    enterpriseId={formData.enterprise}
                    vehicleId={formData.vehicle}
                    onChange={(vehicleId) =>
                        setFormData({
                            ...formData,
                            vehicle: vehicleId,
                        })
                    }
                />

                <FormSelect
                    id="frequency"
                    name="frequency"
                    label="Периодичность:"
                    value={formData.frequency ?? ""}
                    onChange={(event) =>
                        setFormData({
                            ...formData,
                            frequency: event.target.value,
                        })
                    }
                    placeholder="Выберите период"
                    items={frequencies}
                    getOptionLabel={(frequency) => frequency.display_name}
                />

                <Button type="submit" disabled={isBuilding}>
                    Сформировать отчет
                </Button>
            </form>

            {canRenderPdf && uuid && (
                <div className="mt-3">
                    <a href={routes.report.pdfApi(report_type, uuid)}>pdf</a>
                </div>
            )}

            {statusText && (
                <div className="mt-3">
                    <Table bordered striped>
                        <tbody>
                            <tr>
                                <td>{statusText}</td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
            )}

            {errorText && (
                <div className="alert alert-danger mt-3">
                    {errorText}
                </div>
            )}

            {rows.length > 0 && (
                <div className="table-responsive mt-3">
                    <Table bordered striped>
                        <thead>
                            <tr>
                                {headers.map((header) => (
                                    <th key={header.name}>{header.verbose_name}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {headers.map((header) => (
                                        <td key={header.name}>
                                            {formatCellValue(header, row)}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </div>
            )}

            {!statusText && !errorText && rows.length === 0 && uuid && (
                <div className="mt-3">
                    <Table bordered striped>
                        <tbody>
                            <tr>
                                <td>Нет данных для отображения</td>
                            </tr>
                        </tbody>
                    </Table>
                </div>
            )}
        </div>
    )
}

export default ReportPage