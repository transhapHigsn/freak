from typing import Any, Dict

from dataclasses import dataclass


@dataclass
class RequestContext:
    """Class for defining structure of request structure."""

    input: Dict[str, Any]
    name: str
    order: int
