from typing import Any, Dict, Optional

from dataclasses import dataclass


@dataclass
class RequestContext:
    """Class for defining structure of request structure."""

    input: Dict[str, Any]


@dataclass
class ResponseContext:
    """Class for defining structure of response structure."""

    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    message: Optional[str] = None
