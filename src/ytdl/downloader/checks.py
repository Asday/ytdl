import subprocess

from django.core.checks import Critical, register


@register()
def check_youtube_dl_is_installed(app_configs, **kwargs):
    error = Critical(
        '`youtube-dl` is not installed.',
        hint='Head to `https://rg3.github.io/youtube-dl/` to get it.',
        id='downloader.E_YOUTUBE_DL_NOT_INSTALLED',
    )

    try:
        return_code = subprocess.check_call(['youtube-dl', '--version'])
    except subprocess.SubprocessError:
        return [error]

    if return_code != 0:
        return [error]

    return []
