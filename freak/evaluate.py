from typing import Type

from freak.models.input import InputModel
from freak.models.request import RequestContext
from freak.models.response import (
    InputErrorsResponseContext,
    Response,
    SuccessResponseContext,
)
from freak.types import FUNC_TYPE
from pydantic import ValidationError


def evaluate_input(
    ctx: RequestContext, required_model: Type[InputModel]
) -> Response:
    try:
        required_model(**ctx.input)
        return SuccessResponseContext(
            input=ctx.input,
            output={},
        )
    except ValidationError as err:
        return InputErrorsResponseContext(
            input=ctx.input, json_errors=err.json()
        )


# def evaluate_output(
#     ctx: Response, required_model: Type[InputModel]
# ) -> Response:
#     try:
#         required_model(**ctx.output)
#         return SuccessResponseContext(
#             input=ctx.output,
#             output={},
#         )
#     except ValidationError as err:
#         return InputErrorsResponseContext(
#             input=ctx.input, json_errors=err.json()
#         )


def executor(
    func: FUNC_TYPE,
    ctx: RequestContext,
    input_model: Type[InputModel],
    # output_model: Type[Any],
) -> Response:
    check_input = evaluate_input(ctx=ctx, required_model=input_model)
    if not check_input.success:
        return check_input

    response = func(ctx=ctx)  # type: ignore

    # TODO: come up with output validation logic.
    # also, see if this is even required.
    # if response.success:
    #     check_output = evaluate_output(ctx=response, required_model=output_model)
    #     if not check_output.success:
    #         return check_output

    return response
