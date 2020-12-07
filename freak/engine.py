from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from importlib import import_module
from inspect import getabsfile

FUNC_TYPE = Callable[..., Dict[str, Any]]
LOCATOR_TYPE = Callable[..., List[Tuple[int, str]]]
ORGANIZER_TYPE = Callable[..., List[Tuple[int, str, FUNC_TYPE]]]


def factory(flow_name: str) -> Dict[str, Union[LOCATOR_TYPE, ORGANIZER_TYPE]]:
    flow_module_name = f"freak.flows.{flow_name}"
    module = import_module(name=flow_module_name)
    return {
        "locator": module.__dict__["locator"],
        "organizer": module.__dict__["organizer"],
        # "decorator": flow_module_name.split["."][-1] # decorator name should be same as file name.
    }


def butler(
    module_name: str,
    decorator_name: str,
    locator: LOCATOR_TYPE,
    organizer: ORGANIZER_TYPE,
    step: int,
) -> List[Tuple[int, str, FUNC_TYPE]]:
    module = import_module(name=module_name)
    file_path = getabsfile(object=module)
    decorators = locator(
        file_path=file_path, decorator=decorator_name, step=step
    )
    funcs = organizer(module=module, funcs=decorators)
    return funcs


def prosecutioner(
    module_name: str,
    decorator_name: str,
    func_args: Tuple[Any, ...],
    func_kwargs: Dict[str, Any],
    step: Optional[int] = None,
) -> List[Dict[str, Any]]:
    tools = factory(flow_name=decorator_name)
    step = step or 1
    funcs = butler(
        module_name=module_name,
        decorator_name=decorator_name,
        locator=tools["locator"],  # type: ignore
        organizer=tools["organizer"],  # type: ignore
        step=step,
    )

    return [func(*func_args, **func_kwargs) for _, _, func in funcs]
