
from taxi_manager.infrastructure.geo_tracking.models import Trip

from django.db.models import Sum

class TripReposipory:
    def mileage_km(self, car_ids,  from_date, to_date, min_mileage_km: float|None):
        rows = (
            Trip.objects
            .filter_vehicles(car_ids)
            .filter_period(from_date, to_date)
            .annotate_path()
            .annotate_mileage()
            .values("vehicle")
            .annotate(mileage=Sum("mileage"))
            .order_by("-mileage")
            .values_list("vehicle", "vehicle__number", "mileage", "vehicle__model__name", named=True)
        )

        if min_mileage_km:
            rows = rows.filter(mileage__gte=min_mileage_km*1000)

        if not rows:
            return []  
        
        return [{"id": row.vehicle, "number": row.vehicle__number, "mileage": row.mileage.km, "model": row.vehicle__model__name} for row in rows]
 
    


