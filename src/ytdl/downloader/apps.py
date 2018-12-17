import json
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess

from django.apps import AppConfig

from .exceptions import (
    NoFilesCreatedError,
    TooManyFilesCreatedError,
    YoutubeDLError,
)


class DownloaderAppConfig(AppConfig):
    name = 'downloader'
    verbose_name = 'Downloader'

    def ready(self):
        from . import checks  # noqa

    @staticmethod
    def get_playlist_info(youtube_id):
        try:
            results = subprocess.check_output([
                'youtube-dl',
                '-j',
                '--flat-playlist',
                'https://www.youtube.com/playlist?list=' + youtube_id,
            ])
        except subprocess.CalledProcessError as exc:
            raise YoutubeDLError(exc)

        return (
            json.loads(line) for line in results.decode().split('\n') if line
        )

    @staticmethod
    def download_video(youtube_id, directory):
        with TemporaryDirectory() as temp_dir:
            try:
                subprocess.run(
                    ['youtube-dl', youtube_id],
                    cwd=temp_dir,
                )
            except subprocess.CalledProcessError as exc:
                raise YoutubeDLError(exc)

            files = os.listdir(temp_dir)

            if len(files) > 1:
                raise TooManyFilesCreatedError(files=files)

            if len(files) == 0:
                raise NoFilesCreatedError()

            filename = files[0]
            shutil.move(os.path.join(temp_dir, filename), directory)

        return filename
