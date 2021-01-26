"""
    On a quick note, parallel flow itself is not a single flow. Every parallel branch
    from the main flow itself will trigger a new flow and will execute independent of
    the main flow.
"""


"""
    Note: Do not remove base_flow import.
"""

from typing import Any, Dict, List, Optional, Tuple

import copy
from concurrent.futures import ThreadPoolExecutor

from freak.engine import Engine
from freak.executor import submit_and_execute_single_job
from freak.flows.base_flow import base_flow as parallel_flow
from freak.flows.locators import Locator
from freak.models.request import RequestContext
from freak.models.response import EngineResponse, Response
from freak.types import Flow


class ParallelFlowEngine(Engine):
    def __init__(
        self, module_name: str, decorator_name: str = "parallel_flow"
    ) -> None:
        super().__init__(module_name=module_name, decorator_name=decorator_name)

    def get_parallels(self, for_step: Optional[str]) -> List[str]:
        """
        predecessor = {
            None: [1, 2, 3],
            1: [4, 5],
            2: [6, 7],
        }
        """
        step_graph = self.flow.predecessor

        next_steps = []
        for steps in step_graph.values():
            if for_step in steps:
                next_steps = steps
                break

        if self.flow.parallels:
            parallel_steps = set(next_steps).intersection(self.flow.parallels)
            parallel_steps = parallel_steps.difference({for_step})
            return list(parallel_steps)

        return []

    def execute_parallels(self, for_step, data, executed_steps):
        parallels = self.get_parallels(for_step=for_step)

        with ThreadPoolExecutor(max_workers=3) as executor:
            for parallel in parallels:
                submit_and_execute_single_job(
                    executor=executor,
                    func=self.execute,
                    job_args=(parallel, data, executed_steps),
                )

    def get_following_steps(
        self, from_step: Optional[str], path_traversed: Dict[str, Any]
    ) -> List[str]:
        step_graph = self.flow.predecessor
        if not from_step:
            # pick up root of flow.
            from_step = step_graph[from_step][0]

        next_steps = step_graph.get(from_step, [])
        next_steps_set = set(next_steps) - self.flow.parallels
        next_steps = list(next_steps_set)

        # bug: last_step == "" can only be true for root step.
        last_step = path_traversed.get("last_step", "")
        if last_step == "" and from_step not in step_graph[None]:
            raise Exception("FlowInitiatedMidwayError")

        if from_step not in step_graph.get(last_step, []) and last_step:
            raise Exception("ExecutionBeforePredecessorError")

        return next_steps

    def get_next_step_uid(
        self, resp_ctx: Response, next_steps: List[str]
    ) -> str:
        if resp_ctx.choice:
            if resp_ctx.choice not in next_steps:
                raise Exception("InvalidChoice")

            return resp_ctx.choice

        assert len(next_steps) == 1

        return next_steps[0]

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

            self.execute_parallels(
                for_step=step.name, data=data, executed_steps=path_traversed
            )
            if not resp_ctx.success:
                break

            path = next_steps.copy()
            if next_steps:
                next_step_uid = self.get_next_step_uid(
                    resp_ctx=resp_ctx, next_steps=next_steps
                )
                path = [next_step_uid]

            path_traversed["traversed"][step.uid] = path
            path_traversed["last_step"] = step.uid

            data = resp_ctx.input

            # this will refer last successfully performed action.
            last_successful_step = step.order

            if not next_steps:
                break

            next_step_uid = self.get_next_step_uid(
                resp_ctx=resp_ctx, next_steps=next_steps
            )

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


def locator(module: object, file_path: str, decorator: str) -> Flow:
    loc = Locator(module=module, file_path=file_path, decorator=decorator)
    flow = loc.locate()

    return flow
