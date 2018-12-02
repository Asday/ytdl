from django.apps import AppConfig


class DownloaderAppConfig(AppConfig):
    name = 'downloader'
    verbose_name = 'Downloader'

    def ready(self):
        from . import checks  # noqa
