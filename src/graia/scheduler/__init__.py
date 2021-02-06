from typing import Iterable, List, Optional
from datetime import datetime

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
    
    def schedule(self, timer: Timer, cancelable: Optional[bool] = False,
        decorators: Optional[List[Decorator]] = None,
        dispatchers: List[BaseDispatcher] = None,
        enableInternalAccess: Optional[bool] = False
    ):
        def wrapper(func):
            task = SchedulerTask(
                func, timer, self.broadcast, self.loop, cancelable,
                dispatchers, decorators, enableInternalAccess
            )
            self.schedule_tasks.append(task)
            task.setup_task()
            return func
        return wrapper