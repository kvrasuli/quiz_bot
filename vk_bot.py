import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
import random
import logging

logger = logging.getLogger('vk_logger')


def answer(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1,1000)
    )


def run_bot(vk_group_token):
    vk_session = vk_api.VkApi(token=vk_group_token)
    vk_api_ = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            answer(event, vk_api_)


if __name__ == "__main__":
    load_dotenv()
    vk_group_token = os.getenv('VK_TOKEN')

    run_bot(vk_group_token)