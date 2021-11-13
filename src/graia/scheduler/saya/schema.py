from dataclasses import dataclass, field
from typing import List

from graia.broadcast.entities.decorator import Decorator
from graia.broadcast.typing import T_Dispatcher
from graia.saya.schema import BaseSchema

from .. import Timer


@dataclass
class SchedulerSchema(BaseSchema):
    timer: Timer
    cancelable: bool = field(default=False)
    decorators: List[Decorator] = field(default_factory=list)
    dispatchers: List[T_Dispatcher] = field(default_factory=list)
