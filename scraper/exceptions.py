"""Exception classes for this package."""


class ScrapeError(Exception):
    def __init__(self, error_code: int):
        self.error_code = error_code


class RequestSendError(ScrapeError):
    def __init__(self):
        super().__init__(1003)


class ResultParseError(ScrapeError):
    def __init__(self):
        super().__init__(1004)
