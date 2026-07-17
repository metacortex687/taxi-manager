from vk_bot.bot_client import VkChatBotClient

def start_vk_bot_service(token, group_id):
   
    vk_bot_client=VkChatBotClient(token, group_id)

    for chat_user_id, text in vk_bot_client.listen():
            vk_bot_client.send(chat_user_id, text)
