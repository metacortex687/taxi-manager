from django.db import models

class VehicleModel(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)


class Enterprise(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)


class ManagerAssignment(models.Model):
    enterprise_uuid = models.UUIDField()
    user_uuid = models.UUIDField()
