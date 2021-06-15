import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv
from unpacker import unpack_questions
import os
import random
import redis
import logging

logger = logging.getLogger('vk_logger')

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)


def handle_new_question_request(event, vk_api, questions, db):
    quiz_question = random.choice(list(questions.keys()))
    db.set(event.user_id, quiz_question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=quiz_question,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def handle_solution_attempt(event, vk_api, questions, db):
    restored_question = db.get(event.user_id).decode()
    correct_answer = questions[restored_question].replace(' (', '.')
    if event.text == correct_answer.split('.')[0]:
        logger.info(f'User {event.user_id} answered correctly!')
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Для следующего вопроса нажми «Новый вопрос».',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )
    else:
        logger.info(f'User {event.user_id} was wrong!')
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )


def resign(event, vk_api, questions, db):
    logger.info(f'User {event.user_id} resigns!')
    restored_question = db.get(event.user_id).decode()
    answer = questions[restored_question].replace(' (', '.').split('.')[0]
    vk_api.messages.send(
        user_id=event.user_id,
        message=f"Правильный ответ - {answer}",
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def run_bot(token, redis_endpoint, redis_port, redis_password, questions):
    bot_db = redis.Redis(
        host=redis_endpoint, port=redis_port, password=redis_password, db=0
    )
    vk_session = vk_api.VkApi(token=token)
    vk_api_ = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api_, questions, bot_db)
            elif event.text == 'Сдаться':
                resign(event, vk_api_, questions, bot_db)
            elif event.text == 'Мой счет':
                pass
            else:
                handle_solution_attempt(event, vk_api_, questions, bot_db)


def main():
    load_dotenv()
    vk_group_token = os.getenv('VK_TOKEN')
    redis_endpoint = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')
    path_to_questions = os.getenv('PATH_TO_QUESTIONS')
    questions = unpack_questions(path_to_questions)
    run_bot(
        vk_group_token, redis_endpoint, redis_port, redis_password, questions
    )


if __name__ == "__main__":
    main()
