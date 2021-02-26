from freak.flows.parallel_flow import parallel_flow
from freak.models.input import InputModel, InputModelB, InputModelC
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext
from freak.provider import EngineProvider
from freak.types import Flow


@parallel_flow(
    name="func_one",
    order=1,
    input_model=InputModel,
    output_model=InputModel,
    uid="func_one",
    parent_uid=None,
)
def func_one(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]

    if b > 5:
        choice = "func_two"
    else:
        choice = "func_three"

    return SuccessResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}, choice=choice
    )


@parallel_flow(
    name="func_two",
    order=2,
    input_model=InputModel,
    output_model=InputModel,
    uid="func_two",
    parent_uid="func_one",
)
def func_two(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 2, "b": b + 3},
    )


@parallel_flow(
    name="func_three",
    order=3,
    input_model=InputModel,
    output_model=InputModel,
    uid="func_three",
    parent_uid="func_one",
    is_parallel=True,
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@parallel_flow(
    name="func_four",
    order=4,
    input_model=InputModelB,
    output_model=InputModelB,
    uid="func_four",
    parent_uid="func_three",
)
def func_four(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    c = ctx.input["c"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 4, "b": b + 5, "c": c + 6},
    )


@parallel_flow(
    name="func_five",
    order=5,
    input_model=InputModelC,
    output_model=InputModelC,
    uid="func_five",
    parent_uid="func_two",
)
def func_five(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    d = ctx.input["d"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 5, "b": b + 6, "d": d + 7},
    )


def test_parallel_flow():
    assert __name__ == "test_parallel_flow"

    engine = EngineProvider(flow_name="parallel_flow").engine

    executioner = engine(module_name=__name__)
    flow_defintion = executioner.flow

    assert isinstance(flow_defintion, Flow) == True

    assert flow_defintion.parallels == {"func_three"}
    assert flow_defintion.predecessor == {
        None: ["func_one"],
        "func_one": ["func_two", "func_three"],
        "func_two": ["func_five"],
        "func_three": ["func_four"],
    }


def test_parallel_flow_prosecutioner():
    engine = EngineProvider(flow_name="parallel_flow").engine
    executioner = engine(module_name=__name__, decorator_name="parallel_flow")

    response = executioner.execute(data={"a": 4, "b": 7}, from_step="func_one")

    output, path_traversed = response

    assert path_traversed == {
        "last_step": "func_two",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_five"],
        },
    }

    responses = output.responses

    assert output.from_step == 1
    assert output.to_step == 5

    assert output.last_successful_step == 2

    assert responses[0].output == {"a": 5, "b": 9}
    assert responses[1].output == {"a": 6, "b": 10}

    assert responses[2].success == False
    assert responses[2].output == {}
    assert (
        responses[2].messages[0]
        == "Variable: d | Type: value_error.missing | Message: field required"
    )

    response = executioner.execute(
        data={"a": 4, "b": 7, "d": 5},
        from_step="func_five",
        executed_steps=path_traversed,
    )

    output, path_traversed = response

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 9, "b": 13, "d": 12}

    assert output.last_successful_step == 5
    assert output.from_step == 5
    assert output.to_step == 5

    assert path_traversed == {
        "last_step": "func_five",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_five"],
            "func_five": [],
        },
    }
