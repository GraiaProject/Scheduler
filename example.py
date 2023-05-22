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
