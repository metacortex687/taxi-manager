from ...vehicle.models import Vehicle

from django.db.models import Q
from django_filters import rest_framework as filters



class VehicleFilter(filters.FilterSet):
    q = filters.CharFilter(method="filter_q")

    class Meta:
        model = Vehicle
        fields = []

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(model__name__icontains=value) |
            Q(number__icontains=value)
        )