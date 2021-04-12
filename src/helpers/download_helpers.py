import os
import pathlib

import youtube_dl


def save_html(html_content, path, filename):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    full_path = os.path.join(path, filename)

    if os.path.exists(full_path):
        return

    with open(full_path, 'w') as file:
        file.write(html_content)


def download_video(video_url, path, filename):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{path}/{filename}.%(ext)s'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
