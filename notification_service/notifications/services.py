from accounts.models import VkAccount
from notification_context.models import ManagerAssignment


def notify_enterprise_managers(
    enterprise_uuid: str,
    notify_text: str,
    vk_bot_client,
) -> None:
    manager_uuids = ManagerAssignment.objects.filter(
        enterprise_uuid=enterprise_uuid,
    ).values_list("user_uuid", flat=True)

    chat_user_ids = VkAccount.objects.filter(
        user_uuid__in=manager_uuids,
    ).values_list("chat_user_id", flat=True)

    for chat_user_id in chat_user_ids:
        vk_bot_client.send(chat_user_id, notify_text)