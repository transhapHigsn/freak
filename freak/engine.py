from typing import Any, Dict, List, Optional, Tuple, Union

from importlib import import_module
from inspect import getabsfile

from freak.models.request import FetchSchemaRequestContext, RequestContext
from freak.models.response import EngineResponse
from freak.types import FUNC_TYPE, LOCATOR_TYPE, ORGANIZER_TYPE, FactoryResult


def factory(flow_name: str) -> FactoryResult:
    flow_module_name = f"freak.flows.{flow_name}"
    module = import_module(name=flow_module_name)
    return FactoryResult(
        locator=module.__dict__["locator"],
        organizer=module.__dict__["organizer"],
    )


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
    data: Dict[str, Any],
    step: Optional[int] = None,
) -> EngineResponse:
    tools = factory(flow_name=decorator_name)
    step = step or 1
    funcs = butler(
        module_name=module_name,
        decorator_name=decorator_name,
        locator=tools.locator,
        organizer=tools.organizer,
        step=step,
    )

    responses = []
    last_successful_step, to_step = step, step
    for order, name, func in funcs:
        ctx = RequestContext(input=data, name=name, order=order)

        resp_ctx = func(ctx=ctx)  # type: ignore
        responses.append(resp_ctx)
        to_step = order  # this will refer to last performed step.
        if not resp_ctx.success:
            break

        data = resp_ctx.input

        # this will refer last successfully performed action.
        last_successful_step = order

    return EngineResponse(
        responses=responses,
        from_step=step,
        to_step=to_step,
        last_successful_step=last_successful_step,
    )


def inspector(
    module_name: str,
    decorator_name: str,
    step: Optional[int] = None,
) -> List[Dict[str, Any]]:
    tools = factory(flow_name=decorator_name)
    step = step or 1
    funcs = butler(
        module_name=module_name,
        decorator_name=decorator_name,
        locator=tools.locator,
        organizer=tools.organizer,
        step=step,
    )

    responses = []
    for order, name, func in funcs:
        ctx = FetchSchemaRequestContext(name=name, order=order)

        resp_ctx = func(ctx=ctx)  # type: ignore
        responses.append(
            {"name": name, "order": order, "schema": resp_ctx.output["schema"]}
        )

    return responses
