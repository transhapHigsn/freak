import abc

from pydantic import BaseModel


class Input(abc.ABC):

    # @abc.abstractmethod
    # def is_valid(self) -> bool:
    #     pass
    pass


class InputModel(BaseModel):
    """Class for defining structure of request data."""

    a: int
    b: int


class InputModelB(BaseModel):
    """Class for defining structure of request data."""

    a: int
    b: int
    c: int
