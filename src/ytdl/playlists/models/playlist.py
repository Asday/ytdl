from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils import timezone

from .video import Video


class Playlist(models.Model):
    added_by = models.ManyToManyField(settings.AUTH_USER_MODEL)

    youtube_id = models.CharField(max_length=34, unique=True)

    def create_and_update_videos(self):
        downloader = apps.get_app_config('downloader')

        now = timezone.now()
        results = {
            result['id']: result
            for result in downloader.get_playlist_info(self.youtube_id)
        }

        for video in self.videos.all():
            result = results.pop(video.youtube_id, None)
            if result is None:
                video.removed = now

                video.save()

                continue

            if result['title'] == video.title:
                continue

            video.deleted = False
            video.privated = False

            if result['title'] == '[Private video]':
                video.privated = True
            elif result['title'] == '[Deleted video]':
                video.deleted = True
            else:
                video.title = result['title']

            video.save()

        # All that's left in `results` will be new stuff.
        Video.objects.bulk_create([
            Video(
                playlist=self,
                youtube_id=result['id'],
                title=result['title'],
                added=now,
                deleted=result['title'] == '[Deleted video]',
                privated=result['title'] == '[Private video]',
            )
            for result in results.values()
        ])
