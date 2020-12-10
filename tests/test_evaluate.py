from freak.evaluate import evaluate_input
from freak.models.input import InputModel
from freak.models.request import RequestContext
from freak.models.response import Response


def test_evaluate_func_success() -> None:
    request = RequestContext(name="test_func", order=-1, input={"a": 1, "b": 2})

    required_model = InputModel
    response = evaluate_input(ctx=request, required_model=required_model)
    assert isinstance(response, Response) == True
    assert response.success == True


def test_evaluate_func_error() -> None:
    request = RequestContext(
        name="test_func", order=-1, input={"a": 1, "c": 2, "b": "a"}
    )

    response = evaluate_input(ctx=request, required_model=InputModel)
    assert isinstance(response, Response) == True
    assert response.success == False
