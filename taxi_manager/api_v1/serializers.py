from rest_framework import serializers
from ..vehicle.models import Vehicle, Model


class VehicleSerializer(serializers.ModelSerializer):
    model_id = serializers.SerializerMethodField()
    enterprise_id = serializers.SerializerMethodField()
    # model_name = serializers.SerializerMethodField()
    # model = ModelSerializer()

    def get_model_id(self,obj):
        return obj.model.id

    def get_enterprise_id(self,obj):
        if not obj.enterprise:
            return None
        return obj.enterprise.id
    
    class Meta:
        #depth = 1
        model = Vehicle
        fields = ("id", "model_id", "number", "vin", "year_of_manufacture", "mileage", "price", "enterprise_id", "created_at", "updated_at",  )


class ModelSerializer(serializers.ModelSerializer):
    type_code = serializers.SerializerMethodField()
    # type_name = serializers.SerializerMethodField()

    def get_type_code(self,obj):
        return obj.type
    
    # def get_type_name(self,obj):
    #     return obj.get_type_display()
   
    class Meta:
        model = Model
        fields = ("id", "name", "type_code", "number_of_seats", "tank_capacity_l", "load_capacity_kg", "created_at", "updated_at", )
