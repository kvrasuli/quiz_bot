import pprint

with open('1vs1200.txt', 'r', encoding='koi8-r') as file:
    content = file.read()

questions_from_file = content.split('\n\n')


questions = dict()
for index, question in enumerate(questions_from_file):
    question = question.lstrip()
    if question.startswith('Вопрос'):
        questions[question] = ''


pprint.pprint(questions)