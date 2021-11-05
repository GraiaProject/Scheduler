"""该模块提供一些便捷的 Timer"""

from datetime import datetime, timedelta
from typing import Optional

from croniter import croniter

from graia.scheduler.utilles import TimeObject, to_datetime


def every(*, base_datetime: Optional[TimeObject] = None, **kwargs):
    if not base_datetime:
        current = datetime.now()
    else:
        current = to_datetime(base_datetime)
    while True:
        current += timedelta(**kwargs)
        yield current


def every_second():
    """每秒钟执行一次"""
    yield from every(seconds=1)


def every_custom_seconds(seconds: int):
    """每 seconds 秒执行一次

    Args:
        seconds (int): 距离下一次执行的时间间隔, 单位为秒
    """
    yield from every(seconds=seconds)


def every_minute():
    """每分钟执行一次."""
    yield from every(minutes=1)


def every_custom_minutes(minutes: int):
    """每 minutes 分执行一次

    Args:
        minutes (int): 距离下一次执行的时间间隔, 单位为分
    """
    yield from every(minutes=minutes)


def every_hours():
    """每小时执行一次."""
    yield from every(hours=1)


def every_custom_hours(hours: int):
    """每 hours 小时执行一次

    Args:
        hours (int): 距离下一次执行的时间间隔, 单位为小时
    """
    yield from every(hours=hours)


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
