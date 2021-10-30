"""该模块提供一些便捷的 Timer"""

from datetime import datetime, timedelta
from typing import Optional

from croniter import croniter

from graia.scheduler.utilles import TimeObject, to_datetime


class Ticker:
    """简单的时间点生成器.

    Attributes:
        start_point (datetime): 开始时间.
        delta (timedelta): 每次偏移的时间.

    Yields:
        datetime: 生成的时间点.
    """

    start_point: datetime
    delta: timedelta

    def __init__(self, base_datetime: Optional[TimeObject] = None, **kwargs):
        self.start_point = (
            datetime.now() if not base_datetime else to_datetime(base_datetime)
        )
        self.delta = timedelta(**kwargs)

    def __iter__(self):
        """生成时间点. 注意, 在本方法调用后, TimeTicker.start_at() 方法对于已开始的迭代无效.

        Yields:
            datetime: 生成的时间点.
        """
        next_exec = self.start_point
        while True:
            next_exec += self.delta
            yield next_exec

    def start_at(self, base_datetime: TimeObject) -> "Ticker":
        """重置开始时间点.

        Args:
            base_datetime (TimeObject): 新的开始时间对象, 若无法推断绝对时间点, 则基于当前 self.start_point 计算.

        Returns:
            Ticker: 返回本对象以允许进一步操作.
        """
        self.start_point = to_datetime(base_datetime, self.start_point)
        return self


def every(**kwargs):
    yield from Ticker(**kwargs)


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
