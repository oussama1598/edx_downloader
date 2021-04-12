import json

import requests
from bs4 import BeautifulSoup


def get_csrf_token():
    response = requests.get('https://courses.edx.org/csrf/api/v1/token')

    if response.status_code != 200:
        return None

    return response.json()['csrfToken']


def login(email, password):
    csrf_token = get_csrf_token()

    if not csrf_token:
        raise Exception('Could not get csrf token from edx')

    response = requests.post(
        'https://courses.edx.org/user_api/v1/account/login_session/',
        headers={
            'x-csrftoken': csrf_token,
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            'referer': 'https://authn.edx.org/',
            'cookie': f'csrftoken={csrf_token};',
        },
        data={
            'email': email,
            'password': password
        }
    )

    if not response.json()['success']:
        raise Exception('Cannot login to edx')

    return response.cookies.get_dict()


def list_courses(cookies):
    response = requests.get(
        'https://courses.edx.org/dashboard',
        cookies=cookies
    )

    parsed_html = BeautifulSoup(response.text, 'html5lib')
    courses = parsed_html.find_all('li', class_='course-item')

    return list(map(
        lambda item: {
            'title': item.find('h3', class_='course-title').text.strip(),
            'link': 'https://learning.edx.org' + item.find('h3', class_='course-title').find('a')['href']
        },
        filter(
            lambda item: item.find('h3', class_='course-title').find('a'),
            courses
        ))
    )


def get_course_blocks(course_id, cookies):
    response = requests.get(
        f'https://courses.edx.org/api/course_home/v1/outline/{course_id}',
        cookies=cookies
    )

    data = response.json()

    return {
        'title': list(data['course_blocks']['blocks'].values())[0]['display_name'],
        'chapters': list(map(
            lambda block: {
                'title': block['display_name'],
                'blocks': block['children']
            },
            filter(
                lambda block: block['type'] == 'chapter',
                data['course_blocks']['blocks'].values()
            )
        ))
    }


def get_block_material(block_id, cookies):
    response = requests.get(
        f'https://courses.edx.org/api/courseware/sequence/{block_id}',
        cookies=cookies
    )

    data = response.json()

    return list(map(
        lambda item: {
            'title': item['page_title'].lower().replace(' ', '_'),
            'type': item['type'],
            'path': item['path'].lower().replace(' ', '_').split('_>_')[:-1],
            'url': f'https://courses.edx.org/xblock/{item["id"]}'
        },
        data['items']
    ))


def get_material_html(url, cookies):
    response = requests.get(
        url,
        cookies=cookies
    )

    return response.text


def get_video_stream_link(url, cookies):
    parsed_html = BeautifulSoup(get_material_html(url, cookies), 'html5lib')
    video_element = parsed_html.find('div', class_='video')
    data = json.loads(video_element['data-metadata'])
    sources = data['sources']
    streams = data['streams']

    if len(sources) == 0:
        return f'https://youtu.be/{streams.split(":")[-1]}'

    return list(filter(
        lambda link: 'mp4' in link,
        sources
    ))[0]
