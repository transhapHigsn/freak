from typing import Any, Dict, List

import abc
import json
from dataclasses import dataclass, field


@dataclass
class Response(abc.ABC):

    input: Dict[str, Any]
    json_errors: str
    messages: List[str]
    output: Dict[str, Any]
    success: bool


@dataclass(frozen=True)
class SuccessResponseContext(Response):
    """Class for defining structure of response structure."""

    input: Dict[str, Any]
    output: Dict[str, Any]  # type: ignore
    success: bool = True
    json_errors: str = ""
    messages: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ErrorResponseContext(Response):
    """Class for defining structure of error response structure."""

    input: Dict[str, Any]
    messages: List[str]  # type: ignore
    json_errors: str = ""
    output: Dict[str, Any] = field(default_factory=dict)
    success: bool = False


@dataclass
class InputErrorsResponseContext(Response):

    input: Dict[str, Any]
    json_errors: str
    messages: List[str] = field(init=False)
    output: Dict[str, Any] = field(default_factory=dict)
    success: bool = False

    def __post_init__(self) -> None:
        errors = json.loads(self.json_errors)
        self.messages = [
            f"{error['type']} {error['loc'][0]} {error['msg']}"
            for error in errors
        ]


@dataclass
class EngineResponse:
    """Class for defining structure of engine response structure."""

    responses: List[Response]
    from_step: int
    to_step: int
    last_successful_step: int
