from dotenv import load_dotenv
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
)
import telegram
import redis
import os
import random
import logging
from enum import Enum
from functools import partial

logger = logging.getLogger('tg_quiz_bot')
logging.basicConfig(level=logging.INFO)

custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)


class State(Enum):
    QUESTION = 1
    ANSWER = 2
    RESIGN = 3


def unpack_questions(path_to_questions):
    with open(path_to_questions, 'r', encoding='koi8-r') as file:
        quiz_content = file.read()
    questions_from_file = quiz_content.split('\n\n')
    questions = dict()
    for index, question in enumerate(questions_from_file):
        question = question.lstrip()
        if question.startswith('Вопрос'):
            answer = questions_from_file[index + 1].lstrip('Ответ:\n')
            questions[question] = answer
    logger.info('Questions have been unpacked!')
    return questions


def handle_new_question_request(update, context, questions, db):
    if update.message.text == 'Новый вопрос':
        quiz_question = random.choice(list(questions.keys()))
        db.set(update.effective_chat.id, quiz_question)
        update.message.reply_text(quiz_question, reply_markup=reply_markup)
    return State.ANSWER


def handle_solution_attempt(update, context, questions, db):
    user = update.message.from_user
    restored_question = db.get(update.effective_chat.id).decode()
    correct_answer = questions[restored_question].replace(' (', '.')
    if update.message.text == 'Сдаться':
        return State.RESIGN
    elif update.message.text == correct_answer.split('.')[0]:
        logger.info(f'User {user.id} answered correctly!')
        update.message.reply_text(
            'Правильно! Для следующего вопроса нажми «Новый вопрос».'
        )
        return State.QUESTION
    else:
        logger.info(f'User {user.id} was wrong!')
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return State.ANSWER


def resign(update, context, questions, db):
    user = update.message.from_user
    logger.info(f'User {user.id} resigns!')
    restored_question = db.get(update.effective_chat.id).decode()
    answer = questions[restored_question].replace(' (', '.').split('.')[0]
    update.message.reply_text(
        f"Правильный ответ - {answer}"
    )
    return State.QUESTION


def start(update, context):
    user = update.message.from_user
    logger.info(f'User {user.id} started the quiz.')
    update.message.reply_text(
        'Приветствую! Для начала нажми "Новый вопрос".',
        reply_markup=reply_markup
    )
    return State.QUESTION


def cancel(update, context):
    user = update.message.from_user
    logger.info(f'User {user.id} cancelled the quiz.')
    update.message.reply_text(
        'Алибидерчи!', reply_markup=telegram.ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def run_bot(token, redis_endpoint, redis_port, redis_password, questions):
    bot_db = redis.Redis(
        host=redis_endpoint, port=redis_port, password=redis_password, db=0
    )
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.QUESTION: [MessageHandler(
                Filters.text, partial(
                    handle_new_question_request,
                    questions=questions, db=bot_db)
            )],
            State.ANSWER: [MessageHandler(
                Filters.text & ~Filters.command, partial(
                    handle_solution_attempt,
                    questions=questions, db=bot_db)
            )],
            State.RESIGN: [MessageHandler(
                Filters.text, partial(resign, questions=questions, db=bot_db)
            )],
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )
    dp.add_handler(conv_handler)

    logger.info('The bot is about to start!')
    updater.start_polling()
    updater.idle()


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_endpoint = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')
    path_to_questions = os.getenv('PATH_TO_QUESTIONS')
    questions = unpack_questions(path_to_questions)
    run_bot(
        telegram_token, redis_endpoint, redis_port, redis_password, questions
    )


if __name__ == '__main__':
    main()
