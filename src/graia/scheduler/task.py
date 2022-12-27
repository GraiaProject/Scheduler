import asyncio
import traceback
from datetime import datetime
from typing import Any, Callable, Generator, List, Optional, Tuple, Awaitable

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
    task: Optional[asyncio.Task]

    broadcast: Broadcast
    dispatchers: List[T_Dispatcher]
    decorators: List[Decorator]

    cancelable: bool
    stopped: bool

    sleep_record: EnteredRecord
    run_record: EnteredRecord

    loop: asyncio.AbstractEventLoop

    @property
    def is_sleeping(self) -> bool:
        return self.sleep_record.entered

    @property
    def is_executing(self) -> bool:
        return self.run_record.entered and not self.sleep_record.entered

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
        self.task = None
        self.stopped = False
        self.dispatchers = dispatchers or []
        self.decorators = decorators or []
        self.sleep_record = EnteredRecord()
        self.run_record = EnteredRecord()

    def setup_task(self) -> asyncio.Task:
        """将本 SchedulerTask 作为 asyncio.Task 排入事件循环."""
        if self.task:
            raise AlreadyStarted("the scheduler task has been started!")
        self.task = self.loop.create_task(self.run())
        return self.task

    def sleep_interval_generator(self) -> Generator[float, None, None]:
        for next_execute_time in self.timer:
            if self.stopped:
                return
            now = datetime.now()
            if next_execute_time >= now:
                yield (next_execute_time - now).total_seconds()

    def coroutine_generator(self) -> Generator[Tuple[Awaitable[Any], bool], None, None]:
        for sleep_interval in self.sleep_interval_generator():
            yield (asyncio.sleep(sleep_interval), True)
            yield (
                self.broadcast.Executor(
                    target=ExecTarget(
                        callable=self.target,
                        inline_dispatchers=self.dispatchers,
                        decorators=self.decorators,
                    ),
                ),
                False,
            )

    @print_track_async
    async def run(self) -> None:
        if self.run_record.entered:
            raise AlreadyStarted("the scheduler task has been started!")
        with self.run_record:
            for coro, waiting in self.coroutine_generator():
                if waiting:  # 是否为 asyncio.sleep 的 coro
                    with self.sleep_record:
                        try:
                            await coro
                            continue
                        except asyncio.CancelledError:
                            return
                try:
                    await (coro if self.cancelable else asyncio.shield(coro))
                except asyncio.CancelledError:
                    if self.cancelable:
                        return
                    raise
                except (ExecutionStop, PropagationCancelled):
                    pass
                except Exception as e:
                    traceback.print_exc()
                    await self.broadcast.postEvent(ExceptionThrown(e, None))

    def stop_gen_interval(self) -> None:
        if not self.stopped:
            self.stopped = True

    async def join(self, stop: bool = False) -> None:
        """阻塞直至当前 SchedulerTask 执行完毕.

        Args:
            stop (bool, optional): 是否停止当前 SchedulerTask 下一次运行. 默认为 False.
        """
        if stop and not self.stopped:
            self.stop_gen_interval()

        if self.task:
            await self.task
        self.task = None

    def stop(self):
        """停止当前 SchedulerTask."""
        if self.task and not self.task.cancelled():
            self.task.cancel()
