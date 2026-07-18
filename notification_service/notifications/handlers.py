import logging

from notification_context.models import Enterprise, VehicleModel


logger = logging.getLogger(__name__)

def format_vehicle_field_change(
    field: str,
    before_value,
    after_value,
) -> str:
    if field == "enterprise_uuid":
        field = "предприятие"

        before_value = (
            Enterprise.objects.filter(uuid=before_value)
            .values_list("name", flat=True)
            .first()
            or before_value
        )
        after_value = (
            Enterprise.objects.filter(uuid=after_value)
            .values_list("name", flat=True)
            .first()
            or after_value
        )

    if field == "model_uuid":
        field = "модель"

        before_value = (
            VehicleModel.objects.filter(uuid=before_value)
            .values_list("name", flat=True)
            .first()
            or before_value
        )
        after_value = (
            VehicleModel.objects.filter(uuid=after_value)
            .values_list("name", flat=True)
            .first()
            or after_value
        )

    return f"- {field}: {before_value} → {after_value}"

def handle_vehicles(event: dict) -> None:
    before = event["before"]
    after = event["after"]
    vehicle = after or before

    enterprise_name = (
        Enterprise.objects.filter(uuid=vehicle["enterprise_uuid"])
        .values_list("name", flat=True)
        .first()
        or vehicle["enterprise_uuid"]
    )
    model_name = (
        VehicleModel.objects.filter(uuid=vehicle["model_uuid"])
        .values_list("name", flat=True)
        .first()
        or vehicle["model_uuid"]
    )

    message  = []
    message.append(f"Предприятие: {enterprise_name}")

    if event["op"] == "create":
        message.append(f"Добавлен автомобиль: модель {model_name}, номер {vehicle['number']}")

    if event["op"] == "delete":
        message.append(f"Удалён автомобиль: модель {model_name}, номер {vehicle['number']}")

    if event["op"] == "update":
        if before == after:
            print("before == after")
            return ""

        message.append(
            f"Изменена запись автомобиля: модель {model_name}, "
            f"номер {vehicle['number']}"
        )

        for field in before:
            if before[field] != after[field]:
                message.append(format_vehicle_field_change(
                field,
                before[field],
                after[field],
                ))

    logger.info("Обработано %s: %s", "vehicle", event)

    return "\n".join(message)