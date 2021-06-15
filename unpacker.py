import logging
logger = logging.getLogger('unpacker_logger')

def unpack_questions(path_to_questions):
    with open(path_to_questions, 'r', encoding='koi8-r') as file:
        quiz_content = file.read()
    questions_from_file = quiz_content.split('\n\n')
    unpacked_questions = dict()
    for index, question in enumerate(questions_from_file):
        question = question.lstrip()
        if question.startswith('Вопрос'):
            answer = questions_from_file[index + 1].lstrip('Ответ:\n')
            unpacked_questions[question] = answer
    logger.info('Questions have been unpacked!')
    return unpacked_questions
