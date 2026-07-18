import logging

from .models import Enterprise, ManagerAssignment, VehicleModel


logger = logging.getLogger(__name__)


def handle_enterprise(event: dict) -> None:
    before = event["before"]
    after = event["after"]

    if after:
        Enterprise.objects.update_or_create(
            uuid=after["uuid"],
            defaults={"name": after["name"]},
        )

    if before and not after:
        Enterprise.objects.filter(
            uuid=before["uuid"],
        ).delete()

    logger.info("Обработано %s: %s", Enterprise.__name__, event)


def handle_assignment_managers(event: dict) -> None:
    before = event["before"]
    after = event["after"]

    if before:
        ManagerAssignment.objects.filter(
            enterprise_uuid=before["enterprise_uuid"],
            user_uuid=before["user_uuid"],
        ).delete()

    if after:
        ManagerAssignment.objects.get_or_create(
            enterprise_uuid=after["enterprise_uuid"],
            user_uuid=after["user_uuid"],
        )

    logger.info("Обработано %s: %s", ManagerAssignment.__name__, event)


def handle_vehicle_models(event: dict) -> None:
    before = event["before"]
    after = event["after"]

    if after:
        VehicleModel.objects.update_or_create(
            uuid=after["uuid"],
            defaults={"name": after["name"]},
        )

    if before and not after:
        VehicleModel.objects.filter(
            uuid=before["uuid"],
        ).delete()

    logger.info("Обработано %s: %s", VehicleModel.__name__, event)


