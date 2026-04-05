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

    @staticmethod
    def get_content_type_for_model(model):
        return ContentType.objects.get_for_model(model)
    
    @staticmethod
    def get_instance(uuid, model):
        exchange_item = ExchangeItem.objects.filter(
            content_type=ExchangeItem.get_content_type(model), uuid=uuid
        ).first()

        if exchange_item is None:
            return None

        if exchange_item.content_object is None:
            exchange_item.delete()
            return None

        return exchange_item.content_object



