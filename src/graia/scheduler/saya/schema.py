from typing import List
from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.saya.schema import BaseSchema
from dataclasses import dataclass, field
from .. import Timer

@dataclass
class SchedulerSchema(BaseSchema):
    timer: Timer
    cancelable: bool = field(default=False)
    decorators: List[Decorator] = field(default_factory=list)
    dispatchers: List[BaseDispatcher] = field(default_factory=list)
    enableInternalAccess: bool = field(default=False)