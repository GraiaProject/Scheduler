import asyncio
import traceback
from datetime import datetime
from typing import Any, Callable, Generator, List, Optional

from graia.broadcast import Broadcast
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.exectarget import ExecTarget
from graia.broadcast.exceptions import ExecutionStop, PropagationCancelled
from graia.broadcast.typing import T_Dispatcher
from graia.broadcast.builtin.event import ExceptionThrown
from graia.scheduler.exception import AlreadyStarted
from graia.scheduler.utilles import EnteredRecord, print_track_async

from . import Timer


class SchedulerTask:
    target: Callable[..., Any]
    timer: Timer
    task: asyncio.Task

    broadcast: Broadcast
    dispatchers: List[T_Dispatcher]
    decorators: List[Decorator]

    cancelable: bool = False
    stopped: bool = False

    sleep_record: EnteredRecord
    started_record: EnteredRecord

    loop: asyncio.AbstractEventLoop

    @property
    def is_sleeping(self) -> bool:
        return self.sleep_record.entered

    @property
    def is_executing(self) -> bool:
        return not self.sleep_record.entered

    def __init__(
        self,
        target: Callable[..., Any],
        timer: Timer,
        broadcast: Broadcast,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cancelable: bool = False,
        dispatchers: Optional[List[T_Dispatcher]] = None,
        decorators: Optional[List[Decorator]] = None,
    ) -> None:
        self.target = target
        self.timer = timer
        self.broadcast = broadcast
        self.loop = loop or asyncio.get_running_loop()
        self.cancelable = cancelable
        self.dispatchers = dispatchers or []
        self.decorators = decorators or []
        self.sleep_record = EnteredRecord()
        self.started_record = EnteredRecord()

    def setup_task(self) -> None:
        """将本 SchedulerTask 作为 asyncio.Task 排入事件循环."""
        if not self.started_record.entered:  # 还未启动
            self.task = self.loop.create_task(self.run())
        else:
            raise AlreadyStarted("the scheduler task has been started!")

    def sleep_interval_generator(self) -> Generator[float, None, None]:
        for next_execute_time in self.timer:
            if self.stopped:
                return
            now = datetime.now()
            if next_execute_time >= now:
                yield (next_execute_time - now).total_seconds()

    def coroutine_generator(self):
        for sleep_interval in self.sleep_interval_generator():
            yield (asyncio.sleep(sleep_interval), True, sleep_interval)
            yield (
                self.broadcast.Executor(
                    target=ExecTarget(
                        callable=self.target,
                        inline_dispatchers=self.dispatchers,
                        decorators=self.decorators,
                    ),
                ),
                False,
                None,
            )

    @print_track_async
    async def run(self) -> None:
        for coro, waiting, sleep_interval in self.coroutine_generator():
            if waiting:  # 是否为 asyncio.sleep 的 coro
                with self.sleep_record:
                    try:
                        await coro
                    except asyncio.CancelledError:
                        return
            # 执行
            elif self.cancelable:
                try:
                    await coro
                except asyncio.CancelledError:
                    if self.cancelable:
                        return
                    raise
                except (ExecutionStop, PropagationCancelled):
                    pass
                except Exception as e:
                    traceback.print_exc()
                    await self.broadcast.postEvent(ExceptionThrown(e, None))
            else:
                try:
                    await asyncio.shield(coro)
                except (ExecutionStop, PropagationCancelled):
                    pass
                except Exception as e:
                    traceback.print_exc()
                    await self.broadcast.postEvent(ExceptionThrown(e, None))

    def stop_gen_interval(self) -> None:
        if not self.stopped:
            self.stopped = True

    async def join(self, stop=False):
        """阻塞直至当前 SchedulerTask 执行完毕.

        Args:
            stop (bool, optional): 是否停止当前 SchedulerTask 下一次运行. 默认为 False.
        """
        if stop and not self.stopped:
            self.stop_gen_interval()

        if self.task:
            await self.task

    def stop(self):
        """停止当前 SchedulerTask."""
        if not self.task.cancelled():
            self.task.cancel()
