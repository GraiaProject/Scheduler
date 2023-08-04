from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from creart import AbstractCreator, CreateTargetInfo, exists_module, it, mixin

from . import GraiaScheduler

if TYPE_CHECKING:
    from .saya.behaviour import GraiaSchedulerBehaviour


class SchedulerCreator(AbstractCreator):
    targets = (
        CreateTargetInfo(
            module="graia.scheduler",
            identify="GraiaScheduler",
            humanized_name="Graia Scheduler",
            description="<common,graia,scheduler> a simple but powerful scheduler based on asyncio & broadcast control",
            author=["GraiaProject@github"],
        ),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("graia.broadcast")

    @staticmethod
    def create(create_type: type[GraiaScheduler]) -> GraiaScheduler:
        from graia.broadcast import Broadcast

        return create_type(loop=it(asyncio.AbstractEventLoop), broadcast=it(Broadcast))


class SchedulerBehaviourCreator(AbstractCreator):
    targets = (
        CreateTargetInfo(
            module="graia.scheduler.saya.behaviour",
            identify="GraiaSchedulerBehaviour",
            humanized_name="Saya for Graia Scheduler",
            description="<common,graia,scheduler,saya,behaviour> saya support for Graia Scheduler",
            author=["GraiaProject@github"],
        ),
    )

    @staticmethod
    @mixin(SchedulerCreator)
    def available() -> bool:
        return exists_module("graia.saya")

    @staticmethod
    def create(create_type: type[GraiaSchedulerBehaviour]) -> GraiaSchedulerBehaviour:
        scheduler = it(GraiaScheduler)
        return create_type(scheduler)
