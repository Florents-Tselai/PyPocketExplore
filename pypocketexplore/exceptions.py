class PyPocketExploreError(Exception):
    pass


class InvalidTopicError(PyPocketExploreError):
    pass


class TooManyRequestsError(PyPocketExploreError):
    pass
