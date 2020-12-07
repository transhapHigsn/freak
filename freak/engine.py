from typing import Callable, List, Tuple

from importlib import import_module
from inspect import getabsfile


def all_might(
    module_name: str,
    decorator_name: str,
    locator: Callable,
    organizer: Callable,
) -> List[Tuple[int, Callable]]:
    module = import_module(name=module_name)
    file_path = getabsfile(object=module)
    decorators = locator(file_path=file_path, decorator=decorator_name)
    funcs = organizer(module=module, funcs=decorators)
    return funcs
