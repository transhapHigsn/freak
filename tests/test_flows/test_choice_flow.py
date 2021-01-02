import collections

import pytest
from freak.engine import butler, inspector, prosecutioner
from freak.flows.choice_flow import choice_flow, locator, organizer
from freak.models.input import InputModel, InputModelB
from freak.models.request import RequestContext
from freak.models.response import Response, SuccessResponseContext
from freak.types import Step


@choice_flow(
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


@choice_flow(
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


@choice_flow(
    name="func_three",
    order=3,
    input_model=InputModel,
    output_model=InputModel,
    uid="func_three",
    parent_uid="func_one",
)
def func_three(ctx: RequestContext) -> SuccessResponseContext:
    a = ctx.input["a"]
    b = ctx.input["b"]
    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 3, "b": b + 4},
    )


@choice_flow(
    name="func_four",
    order=4,
    input_model=InputModelB,
    output_model=InputModelB,
    uid="func_four",
    parent_uid="func_two",
)
def func_four(ctx: RequestContext) -> Response:
    a = ctx.input["a"]
    b = ctx.input["b"]
    c = ctx.input["c"]

    return SuccessResponseContext(
        input=ctx.input,
        output={"a": a + 4, "b": b + 5, "c": c + 6},
    )


def test_choice_flow():
    assert __name__ == "test_choice_flow"
    flow = butler(
        module_name=__name__,
        decorator_name="choice_flow",
        locator=locator,
        organizer=organizer,
        step=1,
    )
    assert len(flow) == 4

    assert isinstance(flow, collections.deque) == True
    assert isinstance(flow[0], Step) == True

    assert flow[0].name == "func_one"
    assert flow[1].name == "func_two"
    assert flow[2].name == "func_three"
    assert flow[3].name == "func_four"


@pytest.mark.skip
def test_choice_flow_prosecutioner():
    output = prosecutioner(
        module_name=__name__,
        decorator_name="choice_flow",
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
        decorator_name="choice_flow",
        data={"a": 4, "b": 7, "c": 5},
        step=4,
    )

    responses = output.responses
    assert len(responses) == 1
    assert responses[0].output == {"a": 8, "b": 12, "c": 11}

    assert output.last_successful_step == 4
    assert output.from_step == 4
    assert output.to_step == 4


@pytest.mark.skip
def test_choice_flow_fetch_schema():
    responses = inspector(
        module_name=__name__,
        decorator_name="choice_flow",
    )

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

    assert responses[0]["schema"] == input_model_schema
    assert responses[1]["schema"] == input_model_schema
    assert responses[2]["schema"] == input_model_schema
    assert responses[3]["schema"] == input_model_b_schema
