from typing import Any, Deque

from ast import FunctionDef, parse
from collections import defaultdict, deque
from functools import wraps
from inspect import isfunction

from freak.evaluate import executor
from freak.models.request import RequestContext
from freak.models.response import FetchInputSchemaContext, Response
from freak.types import (
    DECORATOR_RESPONSE,
    FIRST_WRAPPER_RESPONSE,
    FUNC_TYPE,
    Flow,
    Step,
    StepCollector,
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


def locator(file_path: str, decorator: str) -> StepCollector:
    with open(file=file_path, mode="rt") as file:
        tree = parse(source=file.read(), filename=file_path)
        predecessor = defaultdict(list)
        successor = {}
        for part in tree.body:
            if not (isinstance(part, FunctionDef) and part.decorator_list):
                continue

            for deco in part.decorator_list:
                if deco.func.id != decorator:  # type: ignore
                    continue

                deco_kws = {
                    kw.arg: kw.value.value
                    for kw in deco.keywords  # type: ignore
                    if kw.arg in ("order", "uid", "parent_uid")
                }

                parent_uid = deco_kws.get("parent_uid", "")
                uid = deco_kws.get("uid")
                if not uid or (parent_uid == "") or not deco_kws.get("order"):
                    raise Exception("InvalidFlowDefintiionError")

                predecessor[parent_uid].append(uid)
                successor[uid] = Step(
                    uid=uid,
                    parent_uid=parent_uid,
                    order=deco_kws["order"],
                    name=part.name,
                )

    return StepCollector(predecessor=predecessor, successor=successor)


def organizer(module: object, collector: StepCollector, step: int) -> Flow:
    predecessor = collector.predecessor
    successor = collector.successor

    current = None

    flow: Deque[Step] = deque()
    while predecessor.get(current):
        # there is an assumption here, only one child of a step is picked.
        # this does not closely resembe real world scenarios where choice type
        # flow can be there. In such cases two possible scenarios that come up are
        # multiple flows working in parallel or choice based flows. there is additional
        # complexity associated with each of them.
        current = predecessor[current][0]
        next = successor[current]
        # this is not a viable solution.
        # trying options to see if anyone can solve my problem.
        if next.order < step:
            continue

        if isfunction(object=module.__dict__[next.name]):
            next.function = module.__dict__[next.name]
            flow.append(next)

    return flow
