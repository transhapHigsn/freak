from typing import Any, Dict

import abc


class Request(abc.ABC):

    name: str
    order: int
    input: Dict[str, Any]


class RequestContext(Request):
    """Class for defining structure of request structure."""

    def __init__(self, input: Dict[str, Any], name: str, order: int) -> None:
        self.input = input
        self.name = name
        self.order = order


class FetchSchemaRequestContext(RequestContext):

    input: Dict[str, Any] = {"fetch_schema": True}

    def __init__(self, name: str, order: int) -> None:
        self.name = name
        self.order = order
