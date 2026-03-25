from django.contrib.gis.db import models

class GeoAddress(models.Model):
    display_name = models.CharField(max_length=500)
    area = models.PolygonField(srid=4326, geography=True)
