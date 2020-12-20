from typing import Any, Dict, List, Optional

from importlib import import_module
from inspect import getabsfile

from freak.models.request import FetchSchemaRequestContext, RequestContext
from freak.models.response import EngineResponse
from freak.types import LOCATOR_TYPE, ORGANIZER_TYPE, FactoryResult, Flow


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
) -> Flow:
    module = import_module(name=module_name)
    file_path = getabsfile(object=module)
    collector = locator(file_path=file_path, decorator=decorator_name)
    flow = organizer(module=module, collector=collector, step=step)
    return flow


def prosecutioner(
    module_name: str,
    decorator_name: str,
    data: Dict[str, Any],
    step: Optional[int] = None,
) -> EngineResponse:
    tools = factory(flow_name=decorator_name)
    step = top_calculator(step=step)
    flow = butler(
        module_name=module_name,
        decorator_name=decorator_name,
        locator=tools.locator,
        organizer=tools.organizer,
        step=step,
    )

    responses = []
    last_successful_step, to_step = step, step
    for _step in flow:
        ctx = RequestContext(input=data, name=_step.name, order=_step.order)

        resp_ctx = _step.function(ctx=ctx)  # type: ignore
        responses.append(resp_ctx)
        to_step = _step.order  # this will refer to last performed step.
        if not resp_ctx.success:
            break

        data = resp_ctx.input

        # this will refer last successfully performed action.
        last_successful_step = _step.order

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
    flow = butler(
        module_name=module_name,
        decorator_name=decorator_name,
        locator=tools.locator,
        organizer=tools.organizer,
        step=step,
    )

    responses = []
    for _step in flow:
        ctx = FetchSchemaRequestContext(name=_step.name, order=_step.order)

        resp_ctx = _step.function(ctx=ctx)  # type: ignore
        responses.append(
            {
                "name": _step.name,
                "order": _step.order,
                "schema": resp_ctx.output["schema"],
            }
        )

    return responses


def top_calculator(step: Optional[int]) -> int:
    return step or 1
