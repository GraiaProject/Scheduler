from datetime import datetime
from typing import Iterable, List, Optional

from graia.broadcast.typing import T_Dispatcher

Timer = Iterable[datetime]

from asyncio import AbstractEventLoop

from graia.broadcast import Broadcast
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.dispatcher import BaseDispatcher

from .task import SchedulerTask


class GraiaScheduler:
    loop: AbstractEventLoop
    schedule_tasks: List[SchedulerTask]
    broadcast: Broadcast

    def __init__(self, loop: AbstractEventLoop, broadcast: Broadcast) -> None:
        self.schedule_tasks = []
        self.loop = loop
        self.broadcast = broadcast

    def schedule(
        self,
        timer: Timer,
        cancelable: bool = False,
        dispatchers: List[T_Dispatcher] = None,
        decorators: Optional[List[Decorator]] = None,
    ):
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
            task.setup_task()
            return func

        return wrapper
