class UnreachableException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class SQSEmptyQueue(Exception):
    def __init__(self, message):
        super().__init__(message)
