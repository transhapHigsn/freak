from typing import List

from itertools import repeat

from networkx import DiGraph
from networkx.algorithms.dag import is_directed_acyclic_graph


def submit_and_execute_single_job(executor, func, job_args):
    future = executor.submit(func, *job_args)
    return future


def validate_flow(step_graph):
    """
    flow must be a DAG.
    """

    edges: List[str] = []
    for key, value in step_graph.items():
        if key is None or not value:
            continue

        edges.extend(zip(repeat(key, len(value)), value))

    graph = DiGraph()
    graph.add_edges_from(edges)

    return is_directed_acyclic_graph(graph)
