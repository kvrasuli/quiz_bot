import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger('vk_logger')

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)


def answer(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
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