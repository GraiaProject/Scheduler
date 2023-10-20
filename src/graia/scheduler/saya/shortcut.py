"""Saya 相关的工具"""
from __future__ import annotations

from datetime import datetime
from typing import (
    Dict,
    Generator,
    Literal,
    Optional,
    Protocol,
    Union,
)

from graia.saya.factory import SchemaWrapper, factory

from .. import Timer
from ..timers import (
    crontabify,
    every_custom_hours,
    every_custom_minutes,
    every_custom_seconds,
)
from ..utilles import TimeObject
from .schema import SchedulerSchema


@factory
def schedule(timer: Union[Timer, str], cancelable: bool = True) -> SchemaWrapper:
    """在当前 Saya Channel 中设置定时任务

    Args:
        timer (Union[Timer, str]): 定时器或者类似 crontab 的定时模板
        cancelable (bool): 是否能够取消定时任务, 默认为 True
    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """

    return lambda _, buffer: SchedulerSchema(
        timer=crontabify(timer) if isinstance(timer, str) else timer, cancelable=cancelable, **buffer
    )


class _TimerProtocol(Protocol):
    def __call__(self, value: int, /, *, base: Optional[TimeObject] = None) -> Generator[datetime, None, None]:
        ...


_TIMER_MAPPING: Dict[str, _TimerProtocol] = {
    "second": every_custom_seconds,
    "minute": every_custom_minutes,
    "hour": every_custom_hours,
}


@factory
def every(
    value: int = 1,
    mode: Literal["second", "minute", "hour"] = "second",
    start: Optional[TimeObject] = None,
    cancelable: bool = True,
) -> SchemaWrapper:
    """在当前 Saya Channel 中设置基本的定时任务

    Args:
        value (int): 时间间隔, 默认为 1
        mode (Literal["second", "minute", "hour"]): 定时模式, 默认为 ’second‘
        start (Optional[Union[datetime, time, str, float]]): 定时起始时间, 默认为 datetime.now()
        cancelable (bool): 是否能够取消定时任务, 默认为 True
    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """

    return lambda _, buffer: SchedulerSchema(
        timer=_TIMER_MAPPING[mode](value, base=start), cancelable=cancelable, **buffer
    )


@factory
def crontab(pattern: str, start: Optional[TimeObject] = None, cancelable: bool = True) -> SchemaWrapper:
    """在当前 Saya Channel 中设置类似于 crontab 模板的定时任务

    Args:
        pattern (str): 类似 crontab 的定时模板
        start (Optional[Union[datetime, time, str, float]]): 定时起始时间, 默认为 datetime.now()
        cancelable (bool): 是否能够取消定时任务, 默认为 True
    Returns:
        Callable[[T_Callable], T_Callable]: 装饰器
    """

    return lambda _, buffer: SchedulerSchema(timer=crontabify(pattern, start), cancelable=cancelable, **buffer)


on_timer = schedule
