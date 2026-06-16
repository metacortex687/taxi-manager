import { useNavigate, useParams } from "react-router-dom"
import VehicleRealtimeMap from "../components/VehicleRealtimeMap"

function VehicleTrackingPage() {
  const { vehicle_id } = useParams()
  const navigate = useNavigate()

  return (
    <>
      <h1>Отслеживание автомобиля</h1>

      <p>
        <button type="button" onClick={() => navigate(-1)}>
          Назад
        </button>
      </p>

      <VehicleRealtimeMap vehicleId={vehicle_id} />
    </>
  )
}

export default VehicleTrackingPage