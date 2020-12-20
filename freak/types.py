from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from collections import deque
from dataclasses import dataclass

from freak.models.request import RequestContext
from freak.models.response import Response

CONTEXT = Dict[str, Any]
FUNC_TYPE = Callable[[RequestContext], Response]
FIRST_WRAPPER_RESPONSE = FUNC_TYPE
DECORATOR_RESPONSE = Callable[[FUNC_TYPE], FUNC_TYPE]

LIST_OF_TUPLE = List[Tuple[int, str]]


@dataclass
class Step:
    uid: str
    parent_uid: Optional[str]
    order: int
    name: str
    function: Optional[FUNC_TYPE] = None


Steps = List[Step]


@dataclass
class StepCollector:
    successor: Dict[str, Step]
    predecessor: Dict[Union[str, None], List[str]]


Flow = Union[deque, Steps]

ORGANIZER_TYPE = Callable[..., Flow]
LOCATOR_TYPE = Callable[..., StepCollector]


@dataclass
class FactoryResult:

    locator: LOCATOR_TYPE
    organizer: ORGANIZER_TYPE
