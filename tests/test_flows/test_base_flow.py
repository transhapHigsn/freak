from typing import Dict, Tuple, Any

from freak.engine import butler, prosecutioner
from freak.flows.base_flow import base_flow, locator, organizer


@base_flow(name="func_one", order=1)
def func_one(a: int, b: int) -> Dict[str, int]:
    return {"a": a + 1, "b": b + 2}


@base_flow(name="func_two", order=2)
def func_two(a: int, b: int) -> Dict[str, int]:
    return {"a": a + 2, "b": b + 3}


@base_flow(name="func_three", order=3)
def func_three(a: int, b: int) -> Dict[str, int]:
    return {"a": a + 3, "b": b + 4}


def test_base_flow():
    assert __name__ == "test_base_flow"
    funcs = butler(
        module_name=__name__,
        decorator_name="base_flow",
        locator=locator,
        organizer=organizer,
        step=1,
    )
    assert len(funcs) == 3

    assert len(funcs[0]) == 3

    assert funcs[0][1] == "func_one"
    assert funcs[1][1] == "func_two"
    assert funcs[2][1] == "func_three"


def test_base_flow_prosecutioner():
    func_args: Tuple[Any, ...] = (4, 7)
    func_kwargs: Dict[Any, Any] = {}

    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        func_args=func_args,
        func_kwargs=func_kwargs,
    )

    assert len(output) == 3
    assert output[0] == {"a": 5, "b": 9}
    assert output[1] == {"a": 6, "b": 10}
    assert output[2] == {"a": 7, "b": 11}
