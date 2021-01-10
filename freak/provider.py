from typing import Any

import inspect
from importlib import import_module


class EngineProvider:
    def __init__(self, flow_name: str) -> None:
        look_here = f"freak.flows.{flow_name}"
        module = import_module(name=look_here)
        self.engine = self.find_engine(module=module)

    def find_engine(self, module: object) -> Any:
        from freak.engine import Engine

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Engine) and cls != Engine:
                return cls
        else:

            return Engine
