from django.core.management import call_command


def test_server_starts(client):
    client.get('/')


def test_checks_pass():
    call_command('check')


def test_get_playlist_info_raises_for_garbage_playlist():
    downloader = apps.get_app_config('downloader')

    with pytest.raises(YoutubeDLError):
        downloader.get_playlist_info('asdf')


_TEST_PLAYLIST_ID = 'PL59FEE129ADFF2B12'


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
