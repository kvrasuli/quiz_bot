from pathlib import Path
import logging

logger = logging.getLogger(__file__)


def unpack_questions(path_to_questions):
    unpacked_questions = dict()
    for filename in Path(path_to_questions).iterdir():
        with open(filename, 'r', encoding='koi8-r') as file:
            quiz_content = file.read()
        questions_from_file = quiz_content.split('\n\n') 
        for index, question in enumerate(questions_from_file):
            question = question.lstrip()
            if question.startswith('Вопрос'):
                answer = questions_from_file[index + 1].lstrip('Ответ:\n')
                unpacked_questions[question] = answer
    logger.info(f'Total {len(unpacked_questions)} questions unpacked!')
    return unpacked_questions


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unpack_questions('questions')
