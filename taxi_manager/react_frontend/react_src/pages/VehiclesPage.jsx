import { useQuery } from "@tanstack/react-query"
import { fetchDataJSON } from "../api/fetch-data"
import { Link, useParams } from "react-router-dom"
import routes from "../routes"
import {Table} from 'react-bootstrap'

function VehiclesPage() {
    const { enterprise_id } = useParams()
    console.log("!!!!!!!!!!!!!!!!!!!!!!!")
    console.log(enterprise_id)
    console.log(routes.vehicles.api(enterprise_id))


    const query = useQuery({
        queryKey: ["vehicles", enterprise_id],
        queryFn: async () => (await fetchDataJSON(routes.vehicles.api(enterprise_id))).results
    }
    )

    if (query.isPending) {
        return <p>Загрузка...</p>
    }

    if (query.isError) {
        return <p>Ошибка: {query.error.message}</p>
    }

    console.log(query.data)
    return (
        <Table className="table-striped">
            <thead>
                <tr>
                    <th scope="col">Брэнд</th>
                    <th scope="col">Год</th>
                    <th scope="col">Цвет</th>
                    <th scope="col">Цена</th>
                    <th scope="col">Номер</th>
                    <th scope="col">VIN</th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody>
                {query.data.map((vehicle) => (
                    <tr key={vehicle.id}>
                        <td>{vehicle.model__name}</td>
                        <td>{vehicle.year_of_manufacture}</td>
                        <td>{vehicle.color}</td>
                        <td>{vehicle.price}</td>
                        <td>{vehicle.number}</td>
                        <td>{vehicle.vin}</td>
                        <td><a href="/vehicles/${record.id}/edit/">Редактировать</a></td>
                    </tr>
                ))}

            </tbody>
        </Table>
    )
}


export default VehiclesPage