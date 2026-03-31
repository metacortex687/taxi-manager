from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

import uuid

class ExchangeItem(models.Model):
    uuid = models.UUIDField(default = uuid.uuid4, unique=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.content_type} #{self.object_id} [{self.uuid}]"

    class Meta:
        
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="unique_exchange_object"
            )
        ]
