from freak.engine import butler, inspector, prosecutioner
from freak.flows.base_flow import base_flow, locator, organizer
from freak.models.input import InputModel, InputModelB
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext


@base_flow(
    name="func_one", order=1, input_model=InputModel, output_model=InputModel
)
def func_one(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}
    )


@base_flow(
    name="func_two", order=2, input_model=InputModel, output_model=InputModel
)
def func_two(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 2, "b": b + 3},
    )


@base_flow(
    name="func_three", order=3, input_model=InputModel, output_model=InputModel
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@base_flow(
    name="func_four", order=4, input_model=InputModelB, output_model=InputModelB
)
def func_four(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    c = ctx.input["c"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 4, "b": b + 5, "c": c + 6},
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
    assert len(funcs) == 4

    assert len(funcs[0]) == 3

    assert funcs[0][1] == "func_one"
    assert funcs[1][1] == "func_two"
    assert funcs[2][1] == "func_three"
    assert funcs[3][1] == "func_four"


def test_base_flow_prosecutioner():
    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        data={"a": 4, "b": 7},
    )

    responses = output.responses
    total_steps = output.to_step - output.from_step + 1

    assert output.from_step == 1
    assert output.to_step == 4

    assert total_steps == 4
    assert len(responses) == total_steps

    assert output.last_successful_step == 3

    assert responses[0].output == {"a": 5, "b": 9}
    assert responses[1].output == {"a": 6, "b": 10}
    assert responses[2].output == {"a": 7, "b": 11}

    assert responses[3].success == False
    assert responses[3].output == {}
    assert (
        responses[3].messages[0]
        == "Variable: c | Type: value_error.missing | Message: field required"
    )

    output = prosecutioner(
        module_name=__name__,
        decorator_name="base_flow",
        data={"a": 4, "b": 7, "c": 5},
        step=4,
    )

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 8, "b": 12, "c": 11}

    assert output.last_successful_step == 4
    assert output.from_step == 4
    assert output.to_step == 4


def test_base_flow_fetch_schema():
    responses = inspector(
        module_name=__name__,
        decorator_name="base_flow",
    )

    input_model_schema = InputModel.schema()
    input_model_b_schema = InputModelB.schema()

    assert responses[0]["schema"] == input_model_schema
    assert responses[1]["schema"] == input_model_schema
    assert responses[2]["schema"] == input_model_schema
    assert responses[3]["schema"] == input_model_b_schema
