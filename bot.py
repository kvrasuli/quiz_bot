from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os


def unpack_questions():
    with open('1vs1200.txt', 'r', encoding='koi8-r') as file:
        quiz_content = file.read()

    questions_from_file = quiz_content.split('\n\n')

    questions = dict()
    for index, question in enumerate(questions_from_file):
        question = question.lstrip()
        if question.startswith('Вопрос'):
            questions[question] = questions_from_file[index + 1]


def echo(update, context):
    update.message.reply_text(update.message.text)


def run_bot(token):
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    unpack_questions()
    run_bot(telegram_token)


if __name__ == '__main__':
    main()
