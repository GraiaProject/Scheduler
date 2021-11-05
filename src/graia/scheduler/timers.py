"""该模块提供一些便捷的 Timer"""

from datetime import datetime, timedelta
from typing import Generator, Optional

from croniter import croniter

from graia.scheduler.utilles import TimeObject, to_datetime


def every(
    *, base_datetime: Optional[TimeObject] = None, **kwargs
) -> Generator[datetime, None, None]:
    """一个简便的 datetime 生成器.

    Args:
        base_datetime (Optional[TimeObject], optional): 若为 None (默认), 则会相对于当前时间推算. 否则基于 base_datetime 推算.

    Yields:
        datetime: 生成的 datetime.
    """
    if base_datetime is None:
        relative = True
    else:
        relative = False
    if relative:
        while True:
            yield datetime.now() + timedelta(**kwargs)
    else:
        current = to_datetime(base_datetime)
        while True:
            current += timedelta(**kwargs)
            yield current


def every_second(*, base_datetime: Optional[TimeObject] = None):
    """每秒钟执行一次"""
    yield from every(seconds=1, base_datetime=base_datetime)


def every_custom_seconds(seconds: int, *, base_datetime: Optional[TimeObject] = None):
    """每 seconds 秒执行一次

    Args:
        seconds (int): 距离下一次执行的时间间隔, 单位为秒
    """
    yield from every(seconds=seconds, base_datetime=base_datetime)


def every_minute(*, base_datetime: Optional[TimeObject] = None):
    """每分钟执行一次."""
    yield from every(minutes=1, base_datetime=base_datetime)


def every_custom_minutes(minutes: int, *, base_datetime: Optional[TimeObject] = None):
    """每 minutes 分执行一次

    Args:
        minutes (int): 距离下一次执行的时间间隔, 单位为分
    """
    yield from every(minutes=minutes, base_datetime=base_datetime)


def every_hours(*, base_datetime: Optional[TimeObject] = None):
    """每小时执行一次."""
    yield from every(hours=1, base_datetime=base_datetime)


def every_custom_hours(hours: int, *, base_datetime: Optional[TimeObject] = None):
    """每 hours 小时执行一次

    Args:
        hours (int): 距离下一次执行的时间间隔, 单位为小时
    """
    yield from every(hours=hours, base_datetime=base_datetime)


def crontabify(pattern: str, base_datetime: Optional[TimeObject] = None):
    """使用类似 crontab 的方式生成计时器

    Args:
        pattern (str): [description]
        base_datetime (Optional[TimeObject], optional): 开始时间. 默认为 datetime.now().

    Yields:
        [type]: [description]
    """
    base_datetime = datetime.now() if not base_datetime else to_datetime(base_datetime)
    crontab_iter = croniter(pattern, base_datetime)
    while True:
        yield crontab_iter.get_next(datetime)
