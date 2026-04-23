import { useQuery } from "@tanstack/react-query"
import { fetchDataJSON } from "../api/fetch-data"
import { Link } from "react-router-dom"

import routes from "../routes"

function EnterprisesPage() {
    const enterprisesQuery = useQuery({
        queryKey: ["enterprises"],
        queryFn: async () => (await fetchDataJSON(routes.enterprises.api())).results
    }
    )

    if (enterprisesQuery.isPending) {
        return <p>Загрузка...</p>
    }

    if (enterprisesQuery.isError) {
        return <p>Ошибка: {enterprisesQuery.error.message}</p>
    }

    console.log(enterprisesQuery.data)
    return (
        <ul>
            {enterprisesQuery.data.map((enterprise) => (
                <li key={enterprise.id}>
                    <a href="/enterprises/${enterprise.id}/edit/"> {enterprise.name} </a>
                    <Link to={routes.vehicles.url(enterprise.id)}> Авто </Link>
                    <Link to={routes.trips.export.url(enterprise.id)}> Скачать поездки  </Link>
                    <Link to={routes.trips.import.url(enterprise.id)}> Загрузить поездки </Link>
                </li>
            ))}
        </ul>
    )
}


export default EnterprisesPage