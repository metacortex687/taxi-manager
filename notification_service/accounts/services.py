import requests
from uuid import UUID

from django.db import transaction

from .models import VkAccount


def get_me(username: str, password: str, auth_api_url: str) -> dict:
    auth_api_url = auth_api_url.rstrip("/")

    response = requests.post(
        f"{auth_api_url}/token/login/",
        data={
            "username": username,
            "password": password,
        },
        timeout=10,
    )

    if not response.ok:
        return None

    token = response.json()["auth_token"]

    response = requests.get(
        f"{auth_api_url}/users/me/",
        headers={
            "Authorization": f"Token {token}",
        },
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


@transaction.atomic
def link_vk_account(
    username: str,
    password: str,
    auth_api_url: str,
    chat_user_id: int,
) -> VkAccount:
    user_data = get_me(
        username=username,
        password=password,
        auth_api_url=auth_api_url,
    )

    if not user_data:
        return None
    
    user_uuid = UUID(str(user_data["uuid"]))

    # Удаляем связь чата с другим пользователем.
    VkAccount.objects.filter(
        chat_user_id=chat_user_id,
    ).exclude(
        user_uuid=user_uuid,
    ).delete()

    account, _ = VkAccount.objects.update_or_create(
        user_uuid=user_uuid,
        defaults={
            "chat_user_id": chat_user_id,
        },
    )

    return account


def logout(chat_user_id: int) -> bool:
    deleted_count, _ = VkAccount.objects.filter(
        chat_user_id=chat_user_id,
    ).delete()

    return deleted_count > 0