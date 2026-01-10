from rest_framework import serializers
from ..vehicle.models import Vehicle, Model


class VehicleSerializer(serializers.ModelSerializer):
    model_id = serializers.SerializerMethodField()
    # model_name = serializers.SerializerMethodField()
    # model = ModelSerializer()

    def get_model_id(self,obj):
        return obj.model.id

    # def get_model_name(self,obj):
    #     return obj.model.name
    
    class Meta:
        #depth = 1
        model = Vehicle
        fields = ("id", "model_id", "number", "vin", "year_of_manufacture", "mileage", "price", "created_at", "updated_at",  )
