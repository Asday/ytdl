import datetime
import os
import subprocess

from django.apps import apps
from django.core.management import call_command

import attr
from freezegun import freeze_time
import pytest
import pytz

from downloader.exceptions import (
    NoFilesCreatedError,
    TooManyFilesCreatedError,
    YoutubeDLError,
)
from playlists.models import Playlist, Video


def test_server_starts(client):
    client.get('/')


def test_checks_pass():
    call_command('check')


def test_get_playlist_info_raises_for_garbage_playlist():
    downloader = apps.get_app_config('downloader')

    with pytest.raises(YoutubeDLError):
        downloader.get_playlist_info('asdf')


_TEST_PLAYLIST_ID = 'PL59FEE129ADFF2B12'
_TEST_VIDEO_ID = '007VM8NZxkI'


def test_get_playlist_info_returns_iterable():
    downloader = apps.get_app_config('downloader')

    results = downloader.get_playlist_info(_TEST_PLAYLIST_ID)

    iter(results)


def test_get_playlist_info_returns_id_and_title_for_all_results():
    downloader = apps.get_app_config('downloader')

    results = downloader.get_playlist_info(_TEST_PLAYLIST_ID)

    for result in results:
        assert 'id' in result
        assert 'title' in result


def test_download_video_raises_for_garbage_video(tmp_path):
    downloader = apps.get_app_config('downloader')

    with pytest.raises(YoutubeDLError):
        downloader.download_video('asdf', tmp_path)


def test_download_video_creates_a_file(tmp_path):
    downloader = apps.get_app_config('downloader')

    filename = downloader.download_video(_TEST_VIDEO_ID, tmp_path)

    expected_path = os.path.join(tmp_path, filename)
    assert os.path.exists(expected_path)

    os.remove(expected_path)


def test_download_video_raises_when_youtube_dl_misbehaves(tmp_path, mocker):
    downloader = apps.get_app_config('downloader')

    def run_factory(files_to_create):
        def run(*args, cwd, **kwargs):
            for i in range(files_to_create):
                open(os.path.join(cwd, str(i)), 'w').close()

        return run

    mocker.patch.object(subprocess, 'run', run_factory(0))

    with pytest.raises(NoFilesCreatedError):
        downloader.download_video(_TEST_VIDEO_ID, tmp_path)

    mocker.patch.object(subprocess, 'run', run_factory(2))

    with pytest.raises(TooManyFilesCreatedError):
        downloader.download_video(_TEST_VIDEO_ID, tmp_path)


@attr.s
class Params(object):
    preexisting = attr.ib()
    playlist_info = attr.ib()
    expected = attr.ib()


now = datetime.datetime(2018, 12, 2, 0, 0, 0, tzinfo=pytz.UTC)
yesterday = datetime.datetime(2018, 12, 1, 0, 0, 0, tzinfo=pytz.UTC)


@freeze_time('2018-12-02 00:00:00.0')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'params',
    [
        Params(  # None preexisting, none new.
            preexisting=[],
            playlist_info=[],
            expected=[],
        ),
        Params(  # None preexisting, one new.
            preexisting=[],
            playlist_info=[{'id': 'testID', 'title': 'Test Title'}],
            expected=[
                {
                    'youtube_id': 'testID',
                    'title': 'Test Title',
                    'added': now,
                    'removed': None,
                },
            ]
        ),
        Params(  # None preexisting, some new.
            preexisting=[],
            playlist_info=[
                {'id': 'testID1', 'title': 'Test Title 1'},
                {'id': 'testID2', 'title': 'Test Title 2'},
            ],
            expected=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': now,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': now,
                    'removed': None,
                },
            ],
        ),
        Params(  # Some preexisting, none new.
            preexisting=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'added': now,
                'removed': None,
            }],
            playlist_info=[{'id': 'testID', 'title': 'Test Title'}],
            expected=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'added': now,
                'removed': None,
            }],
        ),
        Params(  # Some preexisting, one new.
            preexisting=[{
                'youtube_id': 'testID1',
                'title': 'Test Title 1',
                'added': yesterday,
                'removed': None,
            }],
            playlist_info=[
                {'id': 'testID1', 'title': 'Test Title 1'},
                {'id': 'testID2', 'title': 'Test Title 2'},
            ],
            expected=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': yesterday,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': now,
                    'removed': None,
                },
            ],
        ),
        Params(  # Some preexisting, one removed.
            preexisting=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': yesterday,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': yesterday,
                    'removed': None,
                },
            ],
            playlist_info=[{'id': 'testID1', 'title': 'Test Title 1'}],
            expected=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': yesterday,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': yesterday,
                    'removed': now,
                },
            ],
        ),
        Params(  # Some preexisting, one new, one removed.
            preexisting=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': yesterday,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': yesterday,
                    'removed': None,
                },
            ],
            playlist_info=[
                {'id': 'testID1', 'title': 'Test Title 1'},
                {'id': 'testID3', 'title': 'Test Title 3'},
            ],
            expected=[
                {
                    'youtube_id': 'testID1',
                    'title': 'Test Title 1',
                    'added': yesterday,
                    'removed': None,
                },
                {
                    'youtube_id': 'testID2',
                    'title': 'Test Title 2',
                    'added': yesterday,
                    'removed': now,
                },
                {
                    'youtube_id': 'testID3',
                    'title': 'Test Title 3',
                    'added': now,
                    'removed': None,
                },
            ],
        ),
        Params(  # Some preexisting, one renamed.
            preexisting=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'added': yesterday,
                'removed': None,
            }],
            playlist_info=[{'id': 'testID', 'title': 'Renamed'}],
            expected=[{
                'youtube_id': 'testID',
                'title': 'Renamed',
                'added': yesterday,
                'removed': None,
            }],
        ),
        Params(  # Some preexisting, one deleted.
            preexisting=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'added': yesterday,
                'removed': None,
                'deleted': False,
            }],
            playlist_info=[{'id': 'testID', 'title': '[Deleted video]'}],
            expected=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'deleted': True,
                'privated': False,
            }],
        ),
        Params(  # Some preexisting, one made private.
            preexisting=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'added': yesterday,
                'removed': None,
                'privated': False,
            }],
            playlist_info=[{'id': 'testID', 'title': '[Private video]'}],
            expected=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'deleted': False,
                'privated': True,
            }],
        ),
        Params(  # Some preexisting private, one made public.
            preexisting=[{
                'youtube_id': 'testID',
                'title': '[Private video]',
                'added': yesterday,
                'removed': None,
                'privated': True,
            }],
            playlist_info=[{'id': 'testID', 'title': 'Test Title'}],
            expected=[{
                'youtube_id': 'testID',
                'title': 'Test Title',
                'deleted': False,
                'privated': False,
            }],
        ),
        Params(  # None preexisting, one new private, one new deleted.
            preexisting=[],
            playlist_info=[
                {'id': 'testID1', 'title': '[Private video]'},
                {'id': 'testID2', 'title': '[Deleted video]'},
            ],
            expected=[
                {
                    'youtube_id': 'testID1',
                    'title': '[Private video]',
                    'added': now,
                    'removed': None,
                    'deleted': False,
                    'privated': True,
                },
                {
                    'youtube_id': 'testID2',
                    'title': '[Deleted video]',
                    'added': now,
                    'removed': None,
                    'deleted': True,
                    'privated': False,
                },
            ],
        ),
    ],
)
def test_create_and_update_videos(params, mocker):
    playlist = Playlist.objects.create(youtube_id='playlistID')

    for details in params.preexisting:
        Video.objects.create(playlist=playlist, **details)

    downloader = apps.get_app_config('downloader')

    mocker.patch.object(downloader, 'get_playlist_info')
    downloader.get_playlist_info.return_value = (
        item for item in params.playlist_info
    )

    playlist.create_and_update_videos()

    videos = playlist.videos.all()
    for details in params.expected:
        video = videos.get(youtube_id=details['youtube_id'])

        for attr_name, value in details.items():
            assert getattr(video, attr_name) == value

    assert playlist.videos.count() == len(params.expected)
