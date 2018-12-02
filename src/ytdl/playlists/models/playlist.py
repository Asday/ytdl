from django.conf import settings
from django.db import models


class Playlist(models.Model):
    added_by = models.ManyToManyField(settings.AUTH_USER_MODEL)

    youtube_id = models.CharField(max_length=34, unique=True)
