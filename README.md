# Graia Scheduler

一个基于 `asyncio`, 设计简洁, 代码简单的计划任务库, 使用 `loop.create_task` 创建计划任务;  
同时使用生成器特性与 `croniter` 的定时设计, 轻盈而强大.

## Install

```bash
pip install graia-scheduler

# or use pdm
pdm add graia-scheduler
```

## 使用

```python
import asyncio
from launart import Launart
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.scheduler.timers import crontabify
from graia.scheduler.service import SchedulerService

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
scheduler = GraiaScheduler(loop, bcc)


@scheduler.schedule(crontabify("* * * * * *"))
def something_scheduled():
    print("print every second.")


manager = Launart()
manager.add_service(SchedulerService(scheduler))

manager.launch_blocking(loop=loop)

```

因为基于 `BroadcastControl`, 你可以享受使用 `Dispatcher`, `Interrupt`, `Decorator` 的开发体验.
