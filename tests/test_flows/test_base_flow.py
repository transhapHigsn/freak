from typing import Dict

from freak.engine import all_might
from freak.flows.base_flow import base_flow, function_locator, organizer


@base_flow(name="func_one", order=1)
def func_one(a: int, b: int) -> Dict[str, int]:
    return {"a": a, "b": b}


@base_flow(name="func_two", order=2)
def func_two(a: int, b: int) -> Dict[str, int]:
    return {"a": a, "b": b}


@base_flow(name="func_three", order=3)
def func_three(a: int, b: int) -> Dict[str, int]:
    return {"a": a, "b": b}


def test_base_flow():
    assert __name__ == "test_base_flow"
    funcs = all_might(
        module_name=__name__,
        decorator_name="base_flow",
        locator=function_locator,
        organizer=organizer,
    )
    assert len(funcs) == 3

    assert len(funcs[0]) == 3

    assert funcs[0][1] == "func_one"
    assert funcs[1][1] == "func_two"
    assert funcs[2][1] == "func_three"
