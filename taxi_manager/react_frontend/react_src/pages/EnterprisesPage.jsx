import { useQuery } from "@tanstack/react-query"
import { fetchDataJSON } from "../api/fetch-data"
import { Link } from "react-router-dom"

import routes from "../routes"

function EnterprisesPage() {
    const enterprisesQuery = useQuery({
        queryKey: ["enterprises"],
        queryFn: async () => (await fetchDataJSON(routes.enterprises.api())).results,
    })

    if (enterprisesQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (enterprisesQuery.isError) {
        return <p>Ошибка: {enterprisesQuery.error.message}</p>
    }

    return (
        <div className="table-responsive">
            <table className="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Предприятие</th>
                        <th>Автомобили</th>
                        <th>Экспорт поездок</th>
                        <th>Импорт поездок</th>
                    </tr>
                </thead>

                <tbody>
                    {enterprisesQuery.data.map((enterprise) => (
                        <tr key={enterprise.id}>
                            <td>
                                <Link to={routes.enterpriseEdit.url(enterprise.id)}>
                                    {enterprise.name}
                                </Link>
                            </td>

                            <td>
                                <Link to={routes.vehicles.url(enterprise.id)}>
                                    Список
                                </Link>
                            </td>

                            <td>
                                <Link to={routes.trips.export.url(enterprise.id)}>
                                    Скачать поездки
                                </Link>
                            </td>

                            <td>
                                <Link to={routes.trips.import.url(enterprise.id)}>
                                    Загрузить поездки
                                </Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>

    )
}

export default EnterprisesPage