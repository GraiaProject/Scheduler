from typing import Any, Union

from graia.saya.behaviour import Behaviour
from graia.saya.cube import Cube

from graia.scheduler import GraiaScheduler
from graia.scheduler.saya.schema import SchedulerSchema


class GraiaSchedulerBehaviour(Behaviour):
    scheduler: GraiaScheduler

    def __init__(self, scheduler: GraiaScheduler) -> None:
        self.scheduler = scheduler

    def allocate(self, cube: Cube[SchedulerSchema]):
        if isinstance(cube.metaclass, SchedulerSchema):
            self.scheduler.schedule(
                cube.metaclass.timer,
                cube.metaclass.cancelable,
                cube.metaclass.dispatchers,
                cube.metaclass.decorators,
            )(cube.content)
        else:
            return

        return True

    def release(self, cube: Cube) -> Any:
        if isinstance(cube.metaclass, SchedulerSchema):
            target_tasks = list(
                filter(
                    lambda x: x.target is cube.content, self.scheduler.schedule_tasks
                )
            )
            if target_tasks:
                target = target_tasks[0]
                target.stop_gen_interval()
                target.stop()
                self.scheduler.schedule_tasks.remove(target)
        else:
            return

        return True

    uninstall = release