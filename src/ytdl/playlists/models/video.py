from django.db import models


class Video(models.Model):
    playlist = models.ForeignKey(
        'playlists.Playlist',
        on_delete=models.CASCADE,
        related_name='videos',
    )

    youtube_id = models.CharField(max_length=11)
    title = models.CharField(max_length=100)

    added = models.DateTimeField()
    removed = models.DateTimeField(null=True)

    deleted = models.BooleanField(default=False)
    privated = models.BooleanField(default=False)

    downloaded = models.DateTimeField(null=True)
    do_not_download = models.BooleanField(default=False)
