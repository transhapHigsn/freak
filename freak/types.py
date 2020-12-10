from typing import Any, Callable, Dict, List, Tuple

from freak.models.request import RequestContext
from freak.models.response import Response

CONTEXT = Dict[str, Any]
FUNC_TYPE = Callable[[RequestContext], Response]
LOCATOR_TYPE = Callable[..., List[Tuple[int, str]]]
ORGANIZER_TYPE = Callable[..., List[Tuple[int, str, FUNC_TYPE]]]

FIRST_WRAPPER_RESPONSE = FUNC_TYPE
DECORATOR_RESPONSE = Callable[[FUNC_TYPE], FUNC_TYPE]

LIST_OF_TUPLE = List[Tuple[int, str]]
