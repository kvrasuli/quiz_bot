from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
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


def run_bot(token):
    questions = unpack_questions()
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, partial(echo, questions=questions))
    )
    updater.start_polling()
    updater.idle()


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    run_bot(telegram_token)


if __name__ == '__main__':
    main()
