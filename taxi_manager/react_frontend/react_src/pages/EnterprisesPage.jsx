import { useQuery } from "@tanstack/react-query"
import { fetchDataJSON } from "../api/fetch-data"

function EnterprisesPage() {
    const enterprisesQuery = useQuery({
        queryKey: ["enterprises"],
        queryFn: async () => (await fetchDataJSON("/api/v1/enterprises/")).results
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
                    <a href="/enterprises/${enterprise.id}/vehicles/"> Авто </a>
                    <a href="/enterprises/${enterprise.id}/export/trips/"> Скачать поездки </a>
                    <a href="/enterprises/${enterprise.id}/import/trips/"> Загрузить поездки </a>
                </li>
            ))}
        </ul>
    )
}


export default EnterprisesPage