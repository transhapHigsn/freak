from typing import Any, Dict, List, Optional, Tuple

import copy
from importlib import import_module
from inspect import getabsfile

from freak.models.request import FetchSchemaRequestContext, RequestContext
from freak.models.response import EngineResponse
from freak.types import LOCATOR_TYPE, Flow, Step


class Engine:
    def __init__(
        self,
        module_name: str,
        decorator_name: str,
    ) -> None:
        self.locator = self.locator_generator(flow_name=decorator_name)
        self.flow = self.butler_generator(
            locator=self.locator,
            module_name=module_name,
            decorator_name=decorator_name,
        )
        self.module_name = module_name
        self.decorator_name = decorator_name

    def locator_generator(self, flow_name: str) -> LOCATOR_TYPE:
        flow_module_name = f"freak.flows.{flow_name}"
        module = import_module(name=flow_module_name)
        locator: LOCATOR_TYPE = module.__dict__["locator"]
        return locator

    def butler_generator(
        self, module_name: str, decorator_name: str, locator: LOCATOR_TYPE
    ) -> Flow:
        module = import_module(name=module_name)
        file_path = getabsfile(object=module)
        return locator(
            module=module, file_path=file_path, decorator=decorator_name
        )

    def get_step(self, from_step: Optional[str]) -> Step:
        step_definitions = self.flow.successor

        if not from_step:
            # pick up root of flow.
            from_step = self.flow.predecessor[from_step][0]

        step = step_definitions.get(from_step)
        if not step:
            raise Exception("InvalidStepError")
        return step

    def get_following_steps(
        self, from_step: Optional[str], path_traversed: Dict[str, Any]
    ) -> List[str]:
        step_graph = self.flow.predecessor
        if not from_step:
            # pick up root of flow.
            from_step = step_graph[from_step][0]

        next_steps = step_graph.get(from_step, [])
        if len(next_steps) > 1:
            # assert self.parallel is True or self.choice is True
            raise Exception("NotAllowed")

        last_step = path_traversed.get("last_step", "")
        if from_step not in step_graph.get(last_step, []) and last_step:
            raise Exception("CannotExecuteError")

        return next_steps

    def execute(
        self,
        from_step: Optional[str],
        data: Dict[str, Any],
        executed_steps: Dict[str, Any] = {"traversed": {}, "last_step": ""},
    ) -> Tuple[EngineResponse, Dict[str, Any]]:
        path_traversed = copy.deepcopy(executed_steps)

        step = self.get_step(from_step=from_step)
        next_steps = self.get_following_steps(
            from_step=from_step,
            path_traversed=path_traversed,
        )

        responses = []
        last_successful_step, to_step, from_ = (
            step.order,
            step.order,
            step.order,
        )

        while True:
            ctx = RequestContext(input=data, name=step.name, order=step.order)

            resp_ctx = step.function(ctx=ctx)  # type: ignore
            responses.append(resp_ctx)
            to_step = step.order  # this will refer to last performed step.
            if not resp_ctx.success:
                break

            path_traversed["traversed"][step.uid] = next_steps
            path_traversed["last_step"] = step.uid

            data = resp_ctx.input

            # this will refer last successfully performed action.
            last_successful_step = step.order

            if not next_steps:
                break

            next_step_uid = next_steps[0]

            next_steps = self.get_following_steps(
                from_step=next_step_uid,
                path_traversed=path_traversed,
            )
            step = self.get_step(from_step=next_step_uid)

        return (
            EngineResponse(
                responses=responses,
                from_step=from_,
                to_step=to_step,
                last_successful_step=last_successful_step,
            ),
            path_traversed,
        )

    def inspect(
        self,
        from_step: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        responses = []
        path_traversed: Dict[str, Any] = {"traversed": {}, "last_step": ""}

        step = self.get_step(from_step=from_step)
        next_steps = self.get_following_steps(
            from_step=from_step,
            path_traversed=path_traversed,
        )

        while True:
            ctx = FetchSchemaRequestContext(name=step.name, order=step.order)

            resp_ctx = step.function(ctx=ctx)  # type: ignore
            responses.append(
                {
                    "name": step.name,
                    "order": step.order,
                    "schema": resp_ctx.output["schema"],
                }
            )

            path_traversed["traversed"][step.uid] = next_steps
            path_traversed["last_step"] = step.uid

            if not next_steps:
                break

            next_step_uid = next_steps[0]

            next_steps = self.get_following_steps(
                from_step=next_step_uid,
                path_traversed=path_traversed,
            )
            step = self.get_step(from_step=next_step_uid)

        return responses
