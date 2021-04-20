import argparse
from typing import Iterable, Optional, Tuple, cast, Any, Union

from .base import remove_uuid4_prefix


class TupleAction(argparse.Action):
    def __init__(
        self,
        option_strings: Tuple[str, ...],
        dest: str,
        default: Any = None,
        metavar: Optional[Union[Tuple, str]] = None,
        **kwargs,
    ):
        if not isinstance(metavar, tuple):
            ValueError("Metavar must be a tuple for Tuple")
        metavar = cast(Tuple, metavar)
        self.metavar_types = metavar
        # self.metavar_names = tuple([x.__name__.upper() for x in metavar])
        self.metavar_names = tuple([x.__name__.upper() for x in metavar])
        self.name = remove_uuid4_prefix(dest)

        if default:
            # print("metavar", metavar)
            metavar = self.metavar_names
        else:
            metavar = self.name
        if "help" not in kwargs:
            kwargs[
                "help"
            ] = f"provide {len(self.metavar_types)} arguments with corresponding types {self.metavar_names}"

        super(TupleAction, self).__init__(
            option_strings, dest, metavar=metavar, default=default, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        output = []
        try:
            for i, entry_type in enumerate(self.metavar_types):
                output.append(entry_type(values[i]))
            setattr(namespace, self.dest, tuple(output))
        except ValueError as e:
            if option_string:
                parser.error(f"argument {option_string}[{i}]: {str(e)}")
            else:
                parser.error(f"argument {self.name}[{i}]: {str(e)}")


class TypedChoiceAction(argparse.Action):
    def __init__(self, option_strings, dest, choices: Iterable, metavar=None, **kwargs):
        if not choices:
            ValueError("Choices must be set for ChoiceAction")
        self._choices = choices
        metavar = "{" + ",".join([str(x) for x in choices]) + "}"

        if "help" not in kwargs:
            kwargs["help"] = "choose one of the given options"

        super(TypedChoiceAction, self).__init__(
            option_strings, dest, metavar=metavar, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        for entry in self._choices:
            try:
                entry_type = type(entry)
                output = entry_type(values)
                if output == entry:
                    setattr(namespace, self.dest, entry)
                    return
            except ValueError as e:
                pass
        if option_string:
            parser.error(
                f"argument {remove_uuid4_prefix(option_string)}: invalid choice '{values}' (choose from {list(self._choices)})"
            )
        else:
            parser.error(
                f"argument {remove_uuid4_prefix(self.metavar)}: invalid choice '{values}' (choose from {list(self._choices)})"
            )


class BoolAction(argparse.Action):
    def __init__(
        self,
        option_strings: Tuple[str, ...],
        dest: str,
        metavar: Optional[str] = None,
        **kwargs,
    ):
        if not metavar:
            metavar = "{true|false}"
        if not isinstance(metavar, str):
            ValueError("Metavar must be a string")

        if "help" not in kwargs:
            kwargs["help"] = "provide a boolean value (e.g. 'yes', 't', 'false', '0')"

        super(BoolAction, self).__init__(
            option_strings, dest, metavar=metavar, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        yes = ["1", "true", "yes", "on", "t", "y", "yep"]
        no = ["0", "off", "f", "false", "n", "no", "nope"]

        try:
            arg = str(values).lower()
            if arg in yes:
                setattr(namespace, self.dest, True)
                return
            if arg in no:
                setattr(namespace, self.dest, False)
                return
        except ValueError as e:
            parser.error(f"argument {option_string}: {str(e)}")

        parser.error(
            f"argument {remove_uuid4_prefix(self.dest)}: invalid choice '{values}' (choose from {no} / {yes})"
        )
