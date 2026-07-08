import json

from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from taxi_manager.infrastructure.observability.tracing import trace_span
from taxi_manager.infrastructure.vehicle.models import Model




def serialize_model(model: Model) -> dict:
    return {
        "id": model.id,
        "name": model.name,
    }


@csrf_exempt
async def async_model_list_create_view(request):
    if request.method == "GET":
        queryset = Model.objects.all().order_by("id")

        name = request.GET.get("name")
        if name:
            queryset = queryset.filter(name=name)

        results = []

        async for model in queryset:
            results.append(serialize_model(model))

        return JsonResponse(results, safe=False)

    if request.method == "POST":
        with trace_span(
            "AsyncModelListCreateView.post.total",
            stage="view",
            attrs={
                "app.endpoint": "async_models",
                "app.operation": "create_model",
            },
        ):
            with trace_span("AsyncModelListCreateView.post.parse_request", stage="view"):
                try:
                    payload = json.loads(request.body or b"{}")
                except json.JSONDecodeError:
                    return JsonResponse(
                        {"detail": "Invalid JSON."},
                        status=400,
                    )

            with trace_span("AsyncModelListCreateView.post.extract_payload", stage="view"):
                name = payload.get("name")
                type_ = payload.get("type")
                number_of_seats = payload.get("number_of_seats")
                tank_capacity_l = payload.get("tank_capacity_l")
                load_capacity_kg = payload.get("load_capacity_kg")

            with trace_span("AsyncModelListCreateView.post.validate_payload", stage="validation"):
                if not name:
                    return JsonResponse(
                        {"name": ["This field is required."]},
                        status=400,
                    )

                if number_of_seats is None:
                    return JsonResponse(
                        {"number_of_seats": ["This field is required."]},
                        status=400,
                    )

            with trace_span(
                "AsyncModelListCreateView.post.orm_create",
                stage="orm",
                attrs={
                    "db.model": "vehicle_model",
                    "db.operation": "insert",
                },
            ):
                model = await Model.objects.acreate(
                    name=name,
                    type=type_,
                    number_of_seats=number_of_seats,
                    tank_capacity_l=tank_capacity_l,
                    load_capacity_kg=load_capacity_kg,
                )

            with trace_span("AsyncModelListCreateView.post.serialize_response", stage="serialize"):
                data = serialize_model(model)

            with trace_span("AsyncModelListCreateView.post.response_create", stage="response"):
                return JsonResponse(
                    data,
                    status=201,
                )



@csrf_exempt
async def async_model_detail_view(request, pk: int):
    try:
        model = await Model.objects.aget(pk=pk)
    except Model.DoesNotExist:
        raise Http404

    if request.method == "GET":
        return JsonResponse(serialize_model(model))

    if request.method == "DELETE":
        await model.adelete()

        return JsonResponse(
            {},
            status=204,
        )

    return JsonResponse(
        {"detail": "Method not allowed."},
        status=405,
    )