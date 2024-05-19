from pydantic import BaseModel

from implement import source


class InParam:
    ...


class OutParam:
    ...


class CustomType:
    """Docstring for class definition"""

    def __init__(self, value: int):
        """initialize object"""
        self.value = value

    def a_method(self, _in: InParam) -> OutParam:
        """Calculate something"""
        self.x = 1

    def another_method_with_no_docstring(self):
        self.x = 1


def test_extract_class_source():
    code = source._remove_function_body(CustomType)
    assert code == """
class CustomType:
    \"""Docstring for class definition\"""

    def __init__(self, value: int):
        \"""initialize object\"""

    def a_method(self, _in: InParam) -> OutParam:
        \"""Calculate something\"""

    def another_method_with_no_docstring(self):
        ...
""".strip()


class CustomInput:
    """A custom input class."""

    def __init__(self, value: int):
        self.value = value

    def get_value(self) -> int:
        """Get the value of the input."""
        return self.value


class Output:
    """An output class."""

    def __init__():
        pass

    def set_value(self, value: int):
        """Set the value of the output."""
        self.value = value


def calculate(a, b, c: CustomInput) -> Output:
    """Calculate the sum of a, b, and c."""
    # output = Output()
    # output.set_value(a + b + c.get_value())


def test_extract_function_source():
    code = source._remove_function_body(calculate)
    assert code == """def calculate(a, b, c: CustomInput) -> Output:
    \"\"\"Calculate the sum of a, b, and c.\"\"\""""


def test_extract():
    code = source.extract(calculate)
    assert code == """
#class CustomInput:
#    \"""A custom input class.\"""
#
#    def __init__(self, value: int):
#        ...
#
#    def get_value(self) -> int:
#        \"""Get the value of the input.\"""

#class Output:
#    \"""An output class.\"""
#
#    def __init__():
#        ...
#
#    def set_value(self, value: int):
#        \"""Set the value of the output.\"""

def calculate(a, b, c: CustomInput) -> Output:
    \"\"\"Calculate the sum of a, b, and c.\"\"\"
""".strip()


class LinterError(BaseModel):
    file_name: str
    line_number: int
    message: str


def print_error(error: LinterError):
    ...


def print_errors(errors: list[LinterError]):
    ...


def return_none(errors) -> None:
    ...


def function_with_docstring():
    """This is a function with a docstring."""


def test_extract_function_2():
    code = source._remove_function_body(print_error)
    assert code == """def print_error(error: LinterError):\n    ..."""


def test_extract_function_3():
    code = source._remove_function_body(print_errors)
    assert code == """def print_errors(errors: list[LinterError]):\n    ..."""


def test_extract_function_4():
    code = source._remove_function_body(return_none)
    assert code == """def return_none(errors) -> None:\n    ..."""


def test_extract_function_5():
    code = source._remove_function_body(function_with_docstring)
    assert code == """def function_with_docstring():\n    \"""This is a function with a docstring.\"\"\""""
