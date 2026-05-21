
from taxi_manager.infrastructure.geo_tracking.models import Trip

from django.db.models import Sum

class TripReposipory:
    def mileage_km(self, car_id,  from_date, to_date):
        grouped_rows = (
            Trip.objects
            .filter_vehicle(car_id)
            .filter_period(from_date, to_date)
            .annotate_path()
            .annotate_mileage()
            .values("vehicle")
            .annotate(mileage=Sum("mileage"))
            .values_list("vehicle", "mileage", named=True)
        )

        result = list(grouped_rows)
        if not result:
            return 0
        
        return  round(grouped_rows[0].mileage.km, 2)
    


