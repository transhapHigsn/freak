from typing import Any, Dict, List

import abc
import json
from dataclasses import dataclass, field


class Response(abc.ABC):

    input: Dict[str, Any]
    json_errors: str
    messages: List[str]
    output: Dict[str, Any]
    success: bool


class SuccessResponseContext(Response):
    """Class for defining structure of response structure."""

    success: bool = True
    json_errors: str = ""
    messages: List[str] = []

    def __init__(self, input: Dict[str, Any], output: Dict[str, Any]):
        self.input = input
        self.output = output


class ErrorResponseContext(Response):
    """Class for defining structure of error response structure."""

    output: Dict[str, Any] = {}
    success: bool = False
    json_errors: str = ""

    def __init__(self, input: Dict[str, Any], messages: List[str]) -> None:
        self.input = input
        self.messages = messages


class InputErrorsResponseContext(Response):

    messages: List[str] = []
    output: Dict[str, Any] = {}
    success: bool = False

    def __init__(self, input: Dict[str, Any], json_errors: str):
        self.input = input
        self.json_errors = json_errors
        self.messages = InputErrorsResponseContext.get_messages(
            json_errors=json_errors
        )

    @staticmethod
    def get_messages(json_errors: str) -> List[str]:
        errors = json.loads(json_errors)
        return [
            f"Variable: {error['loc'][0]} | Type: {error['type']} | Message: {error['msg']}"
            for error in errors
        ]


class FetchInputSchemaContext(Response):

    messages: List[str] = field(default_factory=list)
    success: bool = field(default=True)
    json_errors: str = field(default="")
    input: Dict[str, Any] = {"fetch_schema": True}

    def __init__(self, output: Dict[str, Any]):
        self.output = output


@dataclass
class EngineResponse:
    """Class for defining structure of engine response structure."""

    responses: List[Response]
    from_step: int
    to_step: int
    last_successful_step: int
