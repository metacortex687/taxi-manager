import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"

import { fetchDataJSON } from "../api/fetch-data"
import routes from "../routes"

function ReportsPage() {
    const reportsQuery = useQuery({
        queryKey: ["reports"],
        queryFn: () => fetchDataJSON(routes.reports.api()),
    })

    if (reportsQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (reportsQuery.isError) {
        return <p>Ошибка: {reportsQuery.error.message}</p>
    }

    const reports = reportsQuery.data ?? []

    return (
        <div>
            <h5>Отчеты:</h5>

            <ul>
                {reports.map((report) => (
                    <li key={report.name}>
                        <Link to={routes.report.url(report.name)}>
                            {report.verbose_name}
                        </Link>
                    </li>
                ))}
            </ul>
        </div>
    )
}

export default ReportsPage