from typing import Any, Callable, Dict, List, Tuple

from importlib import import_module
from inspect import getabsfile

FUNC_TYPE = Callable[..., Dict[str, Any]]


def all_might(
    module_name: str,
    decorator_name: str,
    locator: Callable[..., List[Tuple[int, str]]],
    organizer: Callable[..., List[Tuple[int, str, FUNC_TYPE]]],
) -> List[Tuple[int, str, FUNC_TYPE]]:
    module = import_module(name=module_name)
    file_path = getabsfile(object=module)
    decorators = locator(file_path=file_path, decorator=decorator_name)
    funcs = organizer(module=module, funcs=decorators)
    return funcs
