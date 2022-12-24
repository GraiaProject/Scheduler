from datetime import datetime
from typing import Iterable, List, Optional

from graia.broadcast.typing import T_Dispatcher

Timer = Iterable[datetime]

from asyncio import AbstractEventLoop
import asyncio

from graia.broadcast import Broadcast
from graia.broadcast.entities.decorator import Decorator

from .task import SchedulerTask
from typing import Callable, TypeVar

T_Callable = TypeVar("T_Callable", bound=Callable)


class GraiaScheduler:
    """任务计划器"""

    loop: AbstractEventLoop
    schedule_tasks: List[SchedulerTask]
    broadcast: Broadcast

    def __init__(self, loop: AbstractEventLoop, broadcast: Broadcast) -> None:
        """初始化

        Args:
            loop (AbstractEventLoop): 事件循环
            broadcast (Broadcast): 事件总线
        """
        self.schedule_tasks = []
        self.loop = loop
        self.broadcast = broadcast

    def schedule(
        self,
        timer: Timer,
        cancelable: bool = False,
        dispatchers: Optional[List[T_Dispatcher]] = None,
        decorators: Optional[List[Decorator]] = None,
    ) -> Callable[[T_Callable], T_Callable]:
        """计划一个新任务.

        Args:
            timer (Timer): 该定时任务的计时器.
            cancelable (bool, optional): 能否取消该任务. 默认为 False.
            dispatchers (List[T_Dispatcher], optional): 该任务要使用的 Dispatchers. 默认为空列表.
            decorators (Optional[List[Decorator]], optional): 该任务要使用的 Decorators. 默认为空列表.

        Returns:
            Callable[[T_Callable], T_Callable]: 任务 函数/方法 包装器.
        """

        def wrapper(func):
            task = SchedulerTask(
                func,
                timer,
                self.broadcast,
                self.loop,
                cancelable,
                dispatchers,
                decorators,
            )
            self.schedule_tasks.append(task)
            return func

        return wrapper

    async def run(self) -> None:
        """开始所有计划任务, 在所有任务结束后返回"""
        await asyncio.gather(*(task.setup_task() for task in self.schedule_tasks))

    async def join(self, stop: bool = False) -> None:
        """等待所有计划任务结束"""
        await asyncio.gather(*(task.join(stop=stop) for task in self.schedule_tasks))

    def stop(self) -> None:
        """停止所有计划任务"""
        for task in self.schedule_tasks:
            task.stop()
