import logging

from requests.exceptions import RequestException, ConnectionError
from settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class FailTreeTimeException(RequestException):
    pass


def try_three_time(func):
    def decorator(*args):
        count = 3
        while count:
            try:
                return func(*args)
            except ConnectionError as ex:
                count -= 1
                logger.exception(f'fail calling: {func.__name__}')
            except RequestException as ex:
                logger.exception(f'fail calling: {func.__name__}')
                break
        raise FailTreeTimeException(f'fail calling: {func.__module__}.{func.__name__}')
    return decorator
