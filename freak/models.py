from typing import Any, Dict, List

from dataclasses import dataclass, field


@dataclass
class RequestContext:
    """Class for defining structure of request structure."""

    input: Dict[str, Any]
    name: str
    order: int


@dataclass(frozen=True)
class ResponseContext:
    """Class for defining structure of response structure."""

    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    message: str = ""


@dataclass(frozen=True)
class ErrorResponseContext(ResponseContext):
    """Class for defining structure of error response structure."""

    # below ignore comment shouldn't be required, but somehow it is failing giving error
    # freak/models.py: note: In class "ErrorResponseContext":
    # freak/models.py:29:5: error: Attributes without a default cannot follow attributes with one  [misc]
    #   message: str
    #   ^

    message: str  # type: ignore
    output: Dict[str, Any] = field(default_factory=dict)
    success: bool = False


@dataclass
class EngineResponse:
    """Class for defining structure of engine response structure."""

    responses: List[ResponseContext]
    from_step: int
    to_step: int
    last_successful_step: int
