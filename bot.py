from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import telegram
import redis
import os
import random
from enum import Enum
from functools import partial


custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)


class State(Enum):
    QUESTION = 1
    ANSWER = 2


def unpack_questions():
    with open('1vs1200.txt', 'r', encoding='koi8-r') as file:
        quiz_content = file.read()
    questions_from_file = quiz_content.split('\n\n')
    questions = dict()
    for index, question in enumerate(questions_from_file):
        question = question.lstrip()
        if question.startswith('Вопрос'):
            questions[question] = questions_from_file[index + 1].lstrip('Ответ:\n')
    return questions


def handle_new_question_request(update, context, questions, db):
    if update.message.text == 'Новый вопрос':
        quiz_question = random.choice(list(questions.keys()))
        db.set(update.effective_chat.id, quiz_question)  
        update.message.reply_text(quiz_question, reply_markup=reply_markup)
    return State.ANSWER


def handle_solution_attempt(update, context, questions, db):
    restored_question = db.get(update.effective_chat.id).decode()
    if update.message.text == questions[restored_question].replace(' (', '.').split('.')[0]:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».')
        return State.QUESTION
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return State.ANSWER


def start(update, context):
    update.message.reply_text('Приветствую! Для начала нажми "Новый вопрос".', reply_markup=reply_markup)
    return State.QUESTION


def cancel(update, context):
    update.message.reply_text('Алибидерчи!', reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


def run_bot(token, redis_endpoint, redis_port, redis_password):
    questions = unpack_questions()
    bot_db = redis.Redis(host=redis_endpoint, port=redis_port, password=redis_password, db=0)
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.QUESTION: [MessageHandler(Filters.text, partial(handle_new_question_request, questions=questions, db=bot_db))],
            State.ANSWER: [MessageHandler(Filters.text & ~Filters.command, partial(handle_solution_attempt, questions=questions, db=bot_db))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )
    dp.add_handler(conv_handler)
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
