from django.contrib.gis.db import models
import time
import requests

from django.conf import settings

from django.contrib.gis.geos import Polygon

ADDRESS_BUFFER_SRID = 32637

def make_point_buffer_polygon(point, radius_m):
    metric_point = point.transform(ADDRESS_BUFFER_SRID, clone=True)
    polygon = metric_point.buffer(radius_m)
    polygon.transform(4326)
    return polygon

class GeoAddress(models.Model):
    display_name = models.CharField(max_length=500)
    area = models.PolygonField(srid=4326, geography=True)

    @staticmethod
    def load_address_for_points(points):
        if not points:
            return

        GeoAddress.load_address_for_point(points[0])

        for point in points[1:]:
            GeoAddress.load_address_for_point(point, delay=settings.ADDRESS_PROVIDER["DELAY_REQUEST"] )


    @staticmethod
    def load_address_for_point(point, delay=None):
        if GeoAddress.objects.filter(area__covers=point).exists():
            return
        
        if delay:
            time.sleep(delay)

        
        url = settings.ADDRESS_PROVIDER["URL"] 
        headers = {"accept": "application/json"}
        params = {
            "lat": point.y,
            "lon": point.x,
            "key": settings.ADDRESS_PROVIDER["KEY"],
            "format": "json",
            "accept-language": settings.LANGUAGE_CODE,
        }
        response = requests.get(url, headers=headers, params=params)

        json_data = response.json()

        south = float(json_data["boundingbox"][0])
        north = float(json_data["boundingbox"][1])
        west = float(json_data["boundingbox"][2])
        east = float(json_data["boundingbox"][3])              

        polygon = Polygon((
                (west, south),
                (east, south),
                (east, north),
                (west, north),
                (west, south),
            ), srid=4326
        )

        if not polygon.covers(point):
            polygon = make_point_buffer_polygon(
                point,
                settings.ADDRESS_PROVIDER.get("FALLBACK_RADIUS_M", 50),
            )

        if GeoAddress.objects.filter(area=polygon).exists(): #Избежать повторного внесени в базу
            return
        
        address = json_data["display_name"]
        address = address.replace("Asc","АЗС")
        GeoAddress.objects.create(display_name=address, area = polygon)
        


