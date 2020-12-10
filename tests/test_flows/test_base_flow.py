from freak.engine import butler, prosecutioner
from freak.flows.base_flow import base_flow, locator, organizer
from freak.models import RequestContext, ResponseContext


@base_flow(name="func_one", order=1)
def func_one(ctx: RequestContext) -> ResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return ResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}, success=True
    )


@base_flow(name="func_two", order=2)
def func_two(ctx: RequestContext) -> ResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return ResponseContext(
        input=ctx.input,
        output={"a": a + 2, "b": b + 3},
        success=True,
    )


@base_flow(name="func_three", order=3)
def func_three(ctx: RequestContext) -> ResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return ResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
        success=True,
    )


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
    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        ctx=RequestContext(
            input={"a": 4, "b": 7},
        ),
    )

    assert len(output) == 3
    assert output[0].output == {"a": 5, "b": 9}
    assert output[1].output == {"a": 6, "b": 10}
    assert output[2].output == {"a": 7, "b": 11}
