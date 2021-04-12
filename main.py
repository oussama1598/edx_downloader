import inquirer

from src.modules.edx import Edx
from src.services.config import config


def retrieve_credentials():
    email = config.get('email')
    password = config.get('password')

    if email and password:
        return {
            'email': email,
            'password': password
        }

    answers = inquirer.prompt([
        inquirer.Text('email', message='Please provide your email'),
        inquirer.Text('password', message='Please provide your password'),
    ])

    config.set('email', answers['email'])
    config.set('password', answers['password'])

    return answers


credentials = retrieve_credentials()

edx = Edx(
    credentials['email'],
    credentials['password']
)

edx.login()

courses = edx.list_courses()
course_url = inquirer.prompt([
    inquirer.List(
        'entry',
        message='Select a course: ',
        choices=[
            (course['title'], course['link'])
            for course in courses
        ]
    )
])['entry']

edx.download_course(course_url)
