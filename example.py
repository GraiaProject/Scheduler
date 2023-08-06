from launart import Launart
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler
from graia.scheduler.timers import crontabify
from graia.scheduler.service import SchedulerService
from creart import it

bcc = it(Broadcast)
scheduler = it(GraiaScheduler)


@scheduler.schedule(crontabify("* * * * * *"))
def something_scheduled():
    print("print every second.")


manager = Launart()
manager.add_component(SchedulerService(scheduler))

manager.launch_blocking()
