# taxi_manager/infrastructure/api_v1/serializers/trip_trace.py

from typing import Any

from rest_framework.fields import SerializerMethodField
from rest_framework_gis.fields import GeoJsonDict
from rest_framework_gis.serializers import GeometrySerializerMethodField

from taxi_manager.infrastructure.observability.tracing import trace_span


def get_geometry_attrs(geometry: Any) -> dict[str, Any]:
    attrs: dict[str, Any] = {}

    if geometry is None:
        attrs["geometry.is_none"] = True
        return attrs

    attrs["geometry.is_none"] = False
    attrs["geometry.class"] = geometry.__class__.__name__

    try:
        attrs["geometry.srid"] = geometry.srid
    except Exception:
        pass

    try:
        attrs["geometry.geom_type"] = geometry.geom_type
    except Exception:
        pass

    try:
        attrs["geometry.num_coords"] = len(geometry.coords)
    except Exception:
        pass

    try:
        attrs["geometry.num_points"] = geometry.num_points
    except Exception:
        pass

    return attrs


class TracedGeometrySerializerMethodField(GeometrySerializerMethodField):
    def __init__(
        self,
        *,
        span_name: str,
        stage: str = "serialize",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.span_name = span_name
        self.stage = stage

    def to_representation(self, value):
        with trace_span(
            self.span_name,
            stage=self.stage,
            attrs={
                "input.class": value.__class__.__name__ if value is not None else "",
            },
        ):
            with trace_span(
                f"{self.span_name}.get_geometry_from_method",
                stage=self.stage,
            ):
                geometry = SerializerMethodField.to_representation(self, value)

            if geometry is None:
                return None

            with trace_span(
                f"{self.span_name}.geometry.geojson",
                stage=self.stage,
                attrs=get_geometry_attrs(geometry),
            ) as span:
                geojson = geometry.geojson
                span.set_attribute("geometry.geojson_length", len(geojson))

            with trace_span(
                f"{self.span_name}.GeoJsonDict",
                stage=self.stage,
                attrs={
                    "geometry.geojson_length": len(geojson),
                },
            ):
                return GeoJsonDict(geojson)