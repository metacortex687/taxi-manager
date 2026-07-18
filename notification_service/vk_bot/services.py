from accounts.services import link_vk_account, logout
from vk_bot.bot_client import VkChatBotClient

def start_vk_bot_service(vk_bot_client: VkChatBotClient, token, group_id, auth_api_url):

    for chat_user_id, text in vk_bot_client.listen():
        text = text.strip()
        if not text:
            continue

        if text.startswith("/login"):
            text = text.replace("/login","")
            username, password = text.split()
            result = link_vk_account(username, password, auth_api_url, chat_user_id)
            if not result:
                vk_bot_client.send(chat_user_id, "Неверное имя пользователя или логин.")
                continue
            vk_bot_client.send(chat_user_id, "Вы авторизованы.")
            continue

        if text == "/logout":
            result = logout(chat_user_id)
            if result:
                vk_bot_client.send(chat_user_id, "Вы вышли из аккаунта.")
                continue
            vk_bot_client.send(chat_user_id, "Вы еще не авторизованы.")
            continue

        vk_bot_client.send(chat_user_id, "Авторизация: /login username password")
        vk_bot_client.send(chat_user_id, "Выход из аккаунта: /logout")
        vk_bot_client.send(chat_user_id, "Остальное время оповещение об изменениях с автомобилями")

