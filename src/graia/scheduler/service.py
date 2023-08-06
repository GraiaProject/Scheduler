from typing import Literal, Set
from launart import Service, Launart
from . import GraiaScheduler
import asyncio


class SchedulerService(Service):
    """GraiaScheduler 的 Launart 服务

    Args:
        scheduler (GraiaScheduler): 任务计划器
    """

    id = "scheduler.service"

    def __init__(self, scheduler: GraiaScheduler) -> None:
        super().__init__()
        self.scheduler = scheduler

    @property
    def required(self):
        return set()

    @property
    def stages(self) -> Set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            pass  # Wait for preparation to complete, then we run tasks
        async with self.stage("blocking"):
            tsk = asyncio.create_task(self.scheduler.run())
            await manager.status.wait_for_sigexit()
        async with self.stage("cleanup"):
            # Stop all schedule tasks
            self.scheduler.stop()
            await self.scheduler.join()
            await tsk
