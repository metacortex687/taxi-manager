# taxi_manager/infrastructure/geocoding/tasks.py

from django.conf import settings
from django.contrib.gis.geos import Point
from django.tasks import task


@task(queue_name="geocoding")
def load_geo_addresses(points_payload: list[dict]):
    from taxi_manager.infrastructure.geocoding.models import GeoAddress

    for item in points_payload:
        point = Point(item["lon"], item["lat"], srid=4326)

        GeoAddress.load_address_for_point(
            point,
            delay=settings.ADDRESS_PROVIDER["DELAY_REQUEST"],
        )