from typing import Any, List, Tuple

from ast import FunctionDef, parse
from functools import wraps
from inspect import isfunction

from freak.evaluate import executor
from freak.models.request import RequestContext
from freak.models.response import FetchInputSchemaContext, Response
from freak.types import (
    DECORATOR_RESPONSE,
    FIRST_WRAPPER_RESPONSE,
    FUNC_TYPE,
    LIST_OF_TUPLE,
)


def base_flow(**wkwargs: Any) -> DECORATOR_RESPONSE:
    def wrapper(func: FUNC_TYPE) -> FIRST_WRAPPER_RESPONSE:
        @wraps(func)
        def caller(ctx: RequestContext) -> Response:

            if ctx.input.get("fetch_schema"):
                return FetchInputSchemaContext(
                    output={"schema": wkwargs["input_model"].schema()}
                )

            pre_hook = wkwargs.get("pre_hook")
            if pre_hook:
                pre_hook(ctx=ctx)

            response = executor(
                func=func,
                ctx=ctx,
                input_model=wkwargs["input_model"],
                # output_model=wkwargs["output_model"],
            )

            # response is actually a context object,
            # post hook runs on response of function.
            post_hook = wkwargs.get("post_hook")
            if post_hook:
                post_hook(ctx=ctx)

            return response

        return caller

    return wrapper


def locator(file_path: str, decorator: str, step: int = 1) -> LIST_OF_TUPLE:
    decorators = []
    with open(file=file_path, mode="rt") as file:
        tree = parse(source=file.read(), filename=file_path)
        for part in tree.body:
            if not (isinstance(part, FunctionDef) and part.decorator_list):
                continue

            for deco in part.decorator_list:
                if deco.func.id != decorator:  # type: ignore
                    continue

                deco_kws = {
                    kw.arg: kw.value.value
                    for kw in deco.keywords  # type: ignore
                    if kw.arg == "order"
                }
                if deco_kws["order"] >= step:
                    decorators.append((deco_kws["order"], part.name))

    return decorators


def organizer(
    module: object, funcs: LIST_OF_TUPLE
) -> List[Tuple[int, str, FUNC_TYPE]]:
    func_mapping = [
        (order, func, module.__dict__[func])
        for order, func in funcs
        if isfunction(object=module.__dict__[func])
    ]
    return sorted(func_mapping, key=lambda x: x[0])
