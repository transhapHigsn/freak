from freak.flows.base_flow import base_flow
from freak.models.input import InputModel, InputModelB
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext
from freak.provider import EngineProvider
from freak.types import Flow


@base_flow(
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
    return SuccessResponseContext(
        input=ctx.input, output={"a": a + 1, "b": b + 2}
    )


@base_flow(
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


@base_flow(
    name="func_three",
    order=3,
    input_model=InputModel,
    output_model=InputModel,
    uid="func_three",
    parent_uid="func_two",
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@base_flow(
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


def test_base_flow():
    assert __name__ == "test_base_flow"

    engine = EngineProvider(flow_name="base_flow").engine

    executioner = engine(module_name=__name__, decorator_name="base_flow")
    flow_defintion = executioner.flow

    assert isinstance(flow_defintion, Flow) == True
    assert flow_defintion.predecessor == {
        None: ["func_one"],
        "func_one": ["func_two"],
        "func_two": ["func_three"],
        "func_three": ["func_four"],
    }


def test_base_flow_prosecutioner():
    engine = EngineProvider(flow_name="base_flow").engine
    executioner = engine(module_name=__name__, decorator_name="base_flow")

    response = executioner.execute(data={"a": 4, "b": 7}, from_step="func_one")

    output, path_traversed = response

    assert path_traversed == {
        "last_step": "func_three",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_three"],
            "func_three": ["func_four"],
        },
    }

    responses = output.responses

    assert output.from_step == 1
    assert output.to_step == 4

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

    response = executioner.execute(
        data={"a": 4, "b": 7, "c": 5},
        from_step="func_four",
        executed_steps=path_traversed,
    )

    output, path_traversed = response

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 8, "b": 12, "c": 11}

    assert output.last_successful_step == 4
    assert output.from_step == 4
    assert output.to_step == 4

    assert path_traversed == {
        "last_step": "func_four",
        "traversed": {
            "func_one": ["func_two"],
            "func_two": ["func_three"],
            "func_three": ["func_four"],
            "func_four": [],
        },
    }


def test_base_flow_fetch_schema():
    engine = EngineProvider(flow_name="base_flow").engine
    executioner = engine(module_name=__name__, decorator_name="base_flow")
    responses = executioner.inspect()

    input_model_b_schema = {
        "title": "InputModelB",
        "description": "Class for defining structure of request data.",
        "type": "object",
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "integer"},
            "c": {"title": "C", "type": "integer"},
        },
        "required": ["a", "b", "c"],
    }
    input_model_schema = {
        "title": "InputModel",
        "description": "Class for defining structure of request data.",
        "type": "object",
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "integer"},
        },
        "required": ["a", "b"],
    }

    assert input_model_schema == InputModel.schema()
    assert input_model_b_schema == InputModelB.schema()

    assert executioner.flow.predecessor == responses["graph"]

    schema_info = responses["schema"]

    assert schema_info["func_one"]["schema"] == input_model_schema
    assert schema_info["func_two"]["schema"] == input_model_schema
    assert schema_info["func_three"]["schema"] == input_model_schema
    assert schema_info["func_four"]["schema"] == input_model_b_schema
