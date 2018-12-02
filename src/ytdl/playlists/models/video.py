from django.db import models


class Video(models.Model):
    playlist = models.ForeignKey(
        'playlists.Playlist',
        on_delete=models.CASCADE,
    )

    youtube_id = models.CharField(max_length=11)

    added = models.DateTimeField(null=True)
    removed = models.DateTimeField(null=True)

    downloaded = models.DateTimeField(null=True)
    do_not_download = models.BooleanField(default=False)
