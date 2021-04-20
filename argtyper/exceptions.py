""" Exceptions for ArgTyper """

from typing import Optional, Text, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import ArgParser


class ArgTyperException(Exception):
    """ Thrown on ArgTyper problems """

    ...


class ArgTyperArgumentException(ArgTyperException):
    """ Thrown when something is wrong with a provided Arguement() """

    def __init__(self, func: Callable, argument: str, message: str):
        self.func = func
        self.argument = argument
        super().__init__(
            f"Error while parsing Argument {argument} for function {func.__qualname__}: {message}"
        )


class ArgParserException(Exception):
    """Thrown on Parser errors

    Args:
        parser: The ArgParser instance that raised this errors
        message: Optional error message
    """

    def __init__(self, parser: "ArgParser", message: Optional[Text]):
        self.parser = parser
        self.message = message
        super().__init__(f"{self.parser.prog}: {message}")


class ArgParserExitException(Exception):
    """Thrown when the ArgumentParser would have called sys.exit(<code>)

    Args:
        parser: The ArgParser instance that raised this errors
        status: Status/Exit code of the ArgParser
        message: Optional error message
    """

    def __init__(self, parser: "ArgParser", status: int, message: Optional[Text]):
        self.parser = parser
        self.status = status
        self.message = message
        super().__init__(f"{self.parser.prog} exited with status {status} ({message})")
