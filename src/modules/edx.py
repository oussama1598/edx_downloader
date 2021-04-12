import json
import os

from src.helpers import download_helpers
from src.lib import edx
from src.modules.logger import Logger


class Edx:
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.logger = Logger('EDX-DOWNLOADER')
        self.cookies = {}
        self.cookies_path = os.path.join(os.getcwd(), 'cookies.json')
        self.save_folder = os.path.join(os.getcwd(), 'courses')

    def _save_cookies(self, cookies):
        with open(self.cookies_path, 'w') as file:
            file.write(json.dumps(cookies))

    def _load_cookies(self):
        with open(self.cookies_path, 'r') as file:
            self.cookies = json.load(file)

    def login(self):
        self.logger.info('Logging in to EDX using the provided credentials.')

        if os.path.exists(self.cookies_path):
            self.logger.info(f'Loading saved cookies from {self.cookies_path}.')

            return self._load_cookies()

        self.cookies = edx.login(self.email, self.password)

        self._save_cookies(self.cookies)

    def list_courses(self):
        return edx.list_courses(self.cookies)

    def download_course(self, url):
        self.logger.info(f'Downloading course {url}')

        course_id = url.replace('https://learning.edx.org/courses/', '').split('/')[0]

        course_data = edx.get_course_blocks(
            course_id, self.cookies
        )
        course_title = course_data['title']
        course_chapters = course_data['chapters']

        self.logger.info(f'Found {len(course_chapters)} chapters on this course.')

        for chapter_number, chapter in enumerate(course_chapters):
            chapter_title = f'{chapter_number + 1}___{chapter["title"]}'
            chapter_blocks = chapter['blocks']

            self.logger.info(f'Downloader chapter with name {chapter_title}')

            for block_number, block_id in enumerate(chapter_blocks):
                self.logger.info(f'Fetching block with ID {block_id}')

                materials = edx.get_block_material(block_id, self.cookies)

                for material_number, material in enumerate(materials):
                    material_title = material['title']
                    material_type = material['type']
                    material_path = [course_title] + material['path']
                    material_url = material['url']

                    material_save_path = os.path.join(
                        self.save_folder, course_title, chapter_title, f'{block_number + 1}___' + material_path[-1]
                    )

                    if material_type != 'video':
                        self.logger.info(f'Saving html material to {material_save_path} with title {material_title}')

                        if os.path.exists(f'{material_save_path}/{material_number + 1}___{material_title}.html'):
                            continue

                        download_helpers.save_html(
                            edx.get_material_html(material_url, self.cookies),
                            material_save_path,
                            f'{material_number + 1}___{material_title}.html'
                        )

                    if material_type == 'video':
                        self.logger.info(f'Saving video material to {material_save_path} with title {material_title}')

                        download_helpers.download_video(
                            edx.get_video_stream_link(material_url, self.cookies),
                            material_save_path,
                            f'{material_number + 1}___{material_title}'
                        )
