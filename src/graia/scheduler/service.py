from typing import Literal, Set, List
from launart import Service, Launart
from . import GraiaScheduler
import asyncio


class SchedulerService(Service):
    def __init__(self, *schedulers: GraiaScheduler) -> None:
        self.schedulers: List[GraiaScheduler] = list(schedulers)

    @property
    def required(self):
        return set()

    @property
    def stages(self) -> Set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            pass  # Wait for preparation to complete, then we run tasks

        fut = asyncio.gather(*(sched.run() for sched in self.schedulers))

        async with self.stage("cleanup"):
            # Stop all schedule tasks
            for sched in self.schedulers:
                sched.stop()
            await asyncio.gather(*(sched.join() for sched in self.schedulers))
            await fut
