from typing import Any, Callable, Dict, List, Optional, Tuple

from concurrent.futures import Executor, Future
from itertools import repeat

from freak.models.response import EngineResponse
from networkx import DiGraph
from networkx.algorithms.dag import is_directed_acyclic_graph


def submit_and_execute_single_job(
    executor: Executor,
    func: Callable[..., Tuple[EngineResponse, Dict[str, Any]]],
    job_args: Tuple[str, Any, Dict[str, Any]],
) -> Future:  # type: ignore
    future = executor.submit(func, *job_args)
    return future


def validate_flow(step_graph: Dict[Optional[str], List[str]]) -> bool:
    """
    flow must be a DAG.
    """

    edges: List[str] = []
    for key, value in step_graph.items():
        if key is None or not value:
            continue

        edges.extend(zip(repeat(key, len(value)), value))  # type: ignore

    graph = DiGraph()
    graph.add_edges_from(edges)

    is_dag: bool = is_directed_acyclic_graph(graph)
    return is_dag
