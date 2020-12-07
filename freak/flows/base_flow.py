from typing import Any, Callable, Dict, List, Tuple

from ast import FunctionDef, parse
from functools import wraps
from inspect import isfunction


def base_flow(**wkwargs) -> Callable:
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def caller(*args, **kwargs) -> Dict[str, Any]:
            # pre hook runs on func args & kwargs.
            pre_hook = wkwargs.get("pre_hook")
            if pre_hook:
                pre_hook(*args, **kwargs)

            response = func(*args, **kwargs)

            # post hook runs on response of function.
            post_hook = wkwargs.get("post_hook")
            if post_hook:
                post_hook(**response)

            return response

        return caller

    return wrapper


def function_locator(file_path: str, decorator: str) -> List[Tuple[int, str]]:
    decorators = []
    with open(file=file_path, mode="rt") as file:
        tree = parse(source=file.read(), filename=file_path)
        for part in tree.body:
            if not (isinstance(part, FunctionDef) and part.decorator_list):
                continue

            for deco in part.decorator_list:
                if deco.func.id != decorator:
                    continue

                deco_kws = {
                    kw.arg: kw.value.value
                    for kw in deco.keywords
                    if kw.arg == "order"
                }
                decorators.append((deco_kws.get("order", -1), part.name))

    return decorators


def organizer(
    module: object, funcs: List[Tuple[int, str]]
) -> List[Tuple[int, str, callable]]:
    funcs = [
        (order, func, module.__dict__[func])
        for order, func in funcs
        if isfunction(object=module.__dict__[func])
    ]
    return sorted(funcs, key=lambda x: x[0])
