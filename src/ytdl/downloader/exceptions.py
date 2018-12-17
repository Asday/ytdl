import attr


class YoutubeDLError(Exception):
    pass


@attr.s
class TooManyFilesCreatedError(YoutubeDLError):
    files = attr.ib(default=[], type=list)


class NoFilesCreatedError(YoutubeDLError):
    pass
