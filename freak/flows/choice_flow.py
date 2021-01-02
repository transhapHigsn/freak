from typing import Deque

from collections import deque
from inspect import isfunction

from freak.types import Flow, Step, StepCollector
from freak.utils import generate_hash_for_path

"""
    importing locator and base flow from base flow defintion
    this will act sort of like inheritance, but it is not.
    the implementation of locator and base_flow decorator remains same for both flows.
"""

from freak.flows.base_flow import base_flow as choice_flow
from freak.flows.base_flow import locator


def organizer(module: object, collector: StepCollector, step: int) -> Flow:
    predecessor = collector.predecessor
    successor = collector.successor

    all_paths = get_all_paths(start=None, path=[], route=predecessor)

    choices = {}
    for path in all_paths:
        flow: Deque[Step] = deque(maxlen=len(path))
        for _step in path:
            next = successor[_step]
            if isfunction(object=module.__dict__[next.name]):
                next.function = module.__dict__[next.name]
                flow.append(next)
        choices[generate_hash_for_path(path=path)] = flow

    return choices


def get_paths(start, path, route):
    final_path = []
    if not route.get(start):
        return path

    all_nodes = route[start]
    for node in all_nodes:
        fork_path = path.copy()
        fork_path.append(node)
        cx = get_paths(node, fork_path, route)
        final_path.extend(cx)

    return final_path


def get_all_paths(start, path, route, start_nodes=None):
    if not start_nodes:
        start_nodes = route.get(start, [])

    paths_ = []
    if start is None:
        assert route.get(start, []) == start_nodes
        if len(start_nodes) > 1:
            for node in start_nodes:
                paths_.extend(
                    get_all_paths(
                        start=node, path=[node], route=route, start_nodes=[node]
                    )
                )
            return paths_

    paths = get_paths(start=start, path=path, route=route)

    for node in start_nodes:
        idx = [i for i, val in enumerate(paths) if val == node]
        for i in range(0, len(idx)):
            if i == len(idx) - 1:
                paths_.append(paths[idx[i] :])
            else:
                paths_.append(paths[idx[i] : idx[i + 1]])

    return paths_
