from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import redis
import os
import random
from functools import partial


def unpack_questions():
    with open('1vs1200.txt', 'r', encoding='koi8-r') as file:
        quiz_content = file.read()
    questions_from_file = quiz_content.split('\n\n')
    questions = dict()
    for index, question in enumerate(questions_from_file):
        question = question.lstrip()
        if question.startswith('Вопрос'):
            questions[question] = questions_from_file[index + 1]
    return questions


def echo(update, context, questions):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    if update.message.text == 'Новый вопрос':
        answer = random.choice(list(questions.keys()))
        update.message.reply_text(answer, reply_markup=reply_markup)


def run_bot(token, redis_endpoint, redis_port, redis_password):
    questions = unpack_questions()
    bot_db = redis.Redis(host=redis_endpoint, port=redis_port, password=redis_password, db=0)
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, partial(echo, questions=questions, db=bot_db))
    )
    updater.start_polling()
    updater.idle()


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_endpoint = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')   
    run_bot(telegram_token, redis_endpoint, redis_port, redis_password)


if __name__ == '__main__':
    main()
