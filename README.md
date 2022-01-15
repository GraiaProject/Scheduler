# Graia Scheduler

一个基于 `asyncio`, 设计简洁, 代码简单的计划任务库, 使用 `loop.create_task` 创建计划任务;  
同时使用生成器特性与 `croniter` 的定时设计, 轻盈而强大.

## Install

```bash
pip install graia-scheduler

# or use poetry
poetry add graia-scheduler
```

## 使用

```python
import asyncio
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.scheduler.timers import crontabify

loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
scheduler = GraiaScheduler(loop, bcc)

@scheduler.schedule(crontabify("* * * * * *"))
def something_scheduled():
    print("print every second.")

loop.run_forever()
```

因为基于 `BroadcastControl`, 你可以享受使用 `Dispatcher`, `Interrupt`, `Decorator` 的开发体验.
