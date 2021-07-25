import datetime
import time
from functools import wraps
from loguru import logger

def aware_datetime_now() -> datetime:
    """Возвращает aware datetime в UTC timezone."""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def datetime_to_iso_string(time: datetime.datetime):
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return "{0}:{1}".format(
        timestamp[:-2],
        timestamp[-2:]
    )


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor).
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        next_sleep_time = start_sleep_time

        @wraps(func)
        def inner(*args, **kwargs):
            nonlocal next_sleep_time
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.opt(exception=True).warning('Got exception in backoff:')
                time.sleep(next_sleep_time)
                if next_sleep_time >= border_sleep_time:
                    next_sleep_time = border_sleep_time
                else:
                    next_sleep_time *= factor
                return inner(*args, **kwargs)

        return inner

    return func_wrapper
