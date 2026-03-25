from django.contrib.gis.db import models
import time
import requests

from django.contrib.gis.geos import Polygon

class GeoAddress(models.Model):
    display_name = models.CharField(max_length=500)
    area = models.PolygonField(srid=4326, geography=True)

    @staticmethod
    def load_address_for_points(points):
        if not points:
            return

        GeoAddress.load_address_for_point(points[0])

        for point in points[1:]:
            GeoAddress.load_address_for_point(point, delay=0.1)


    @staticmethod
    def load_address_for_point(point, delay=None):
        if GeoAddress.objects.filter(area__covers=point).exists():
            return
        
        if delay:
            time.sleep(delay)

        
        url = "https://us1.locationiq.com/v1/reverse"
        headers = {"accept": "application/json"}
        params = {
            "lat": point.y,
            "lon": point.x,
            "key": "pk.9baf0d6f3b338ecfe33e0961f069e7ab",
            "format": "json"
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
        GeoAddress.objects.create(display_name=json_data["display_name"], area = polygon)
        


