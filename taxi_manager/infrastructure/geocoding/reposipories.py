
from taxi_manager.infrastructure.geo_tracking.models import Trip

from django.db.models import Sum

class TripReposipory:
    def mileage_km(self, car_ids,  from_date, to_date):
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

        if not rows:
            return []  
        
        return [{"id": row.vehicle, "number": row.vehicle__number, "mileage": row.mileage.km, "model": row.vehicle__model__name} for row in rows]
 
    


