import json
import subprocess

from django.apps import AppConfig

from .exceptions import YoutubeDLError


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
