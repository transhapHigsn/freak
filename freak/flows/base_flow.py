from typing import Any

from functools import wraps

from freak.evaluate import executor
from freak.flows.locators import Locator
from freak.models.request import RequestContext
from freak.models.response import FetchInputSchemaContext, Response
from freak.types import (
    DECORATOR_RESPONSE,
    FIRST_WRAPPER_RESPONSE,
    FUNC_TYPE,
    Flow,
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


def locator(module: object, file_path: str, decorator: str) -> Flow:
    loc = Locator(module=module, file_path=file_path, decorator=decorator)
    return loc.locate()
