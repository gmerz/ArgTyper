""" This file cotains mostly wrappers to convert argparse functionallity to decorators """

import sys
from abc import ABCMeta, abstractmethod
from argparse import Action, ArgumentParser, FileType, HelpFormatter
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NoReturn,
    Optional,
    Text,
    Tuple,
    Type,
    TypeVar,
    Union,
    Literal,
)

from .exceptions import (
    ArgParserException,
    ArgParserExitException,
    ArgTyperException,
    ArgTyperArgumentException,
)


def remove_uuid4_prefix(name):
    if "_" in name and name.index("_") == 32:
        return name[33:]
    else:
        return name


def change_metavar(kwargs, case: Literal["upper", "lower"] = "upper"):
    if "metavar" not in kwargs:
        return
    mvar = kwargs["metavar"]

    if not isinstance(mvar, str):
        return

    if case == "upper":
        kwargs["metavar"] = mvar.upper()
    if case == "lower":
        kwargs["metavar"] = mvar.lower()


class ArgTyperHelpFormatter(HelpFormatter):
    """Help message formatter which uses the argument 'dest' but removes a uuid4 hex value prefix"""

    def _get_default_metavar_for_optional(self, action):
        name = remove_uuid4_prefix(action.dest)
        return name.upper()

    def _get_default_metavar_for_positional(self, action):
        name = remove_uuid4_prefix(action.dest)
        return name


class ArgParser(ArgumentParser):
    """An argument parser that throws exceptions instead of terminating the program


    In the future it might be possible to replace this with the "exit_on_error=False" setting to ArgumentParser (new in python 3.9)
    """

    def __init__(self, *args, **kwargs):
        self._message = ""
        kwargs["formatter_class"] = ArgTyperHelpFormatter
        super().__init__(*args, **kwargs)

    def _print_message(self, message: str, file=None) -> None:
        if message:
            self._message += message  # type: ignore

    def error(self, message: Text) -> NoReturn:
        exc = sys.exc_info()[1]
        if exc:
            raise ArgParserException(self, message) from exc
        raise ArgParserException(self, message)

    def exit(self, status=0, message: Text = None) -> NoReturn:
        if message:
            self._print_message(message)
        exc = sys.exc_info()[1]
        if exc:
            raise ArgParserExitException(self, status, message) from exc
        raise ArgParserExitException(self, status, message)


class DEFAULT(object):
    def __init__(self, value: Any = ...):
        self.value = value


Default = DEFAULT()


_T = TypeVar("_T")


class ArgTyperAttribute(object, metaclass=ABCMeta):
    """ A generic base class for ArgTyper function attributes """

    def __init__(self) -> None:
        if not getattr(self, "arg_options", None):
            self.arg_options: Dict = dict()
        super().__init__()

    _registered_functions: Dict = {}

    @staticmethod
    def _get_unbound_function(func):
        isbound = getattr(func, "__self__", None)
        if isbound:
            func = func.__func__
        return func

    @classmethod
    def _get_attr_for_func(cls, func: Callable):
        """Iterate through functions and parents until we either find the attribute, or can't go further

        This only works if @wraps is used on function wrappers. Conversely, this can be interrupted if a function is wrapped without @wraps.
        """
        while True:
            attribute = cls._registered_functions.get(func, None)
            if attribute:
                return attribute
            isbound = getattr(func, "__self__", None)
            if isbound:
                func = func.__func__  # type: ignore
                continue
            wrapped = getattr(func, "__wrapped__", None)
            if wrapped:
                func = wrapped
                continue
            return None

    @classmethod
    def get(cls, func: Callable, raise_exc: bool = False, default: Any = None):
        """Get an existing attribute for a function.

        If the function does not have this attribute set `default` will be returned

        Args:
            func: The callable for which we want to retrieve this ArgTyper attribute
            raise_exc: If set to `True`, this will raise an exception, if the function does not have this attribute set
            default: The default value to return, in case we don't find the element and do not raise an exception
        """
        if getattr(func, "__self__", None):
            func = func.__func__  # type: ignore
        existing = cls._get_attr_for_func(func)
        if existing:
            return existing
        if raise_exc:
            raise ArgTyperException(f"Callable {func} is no registered command")
        return default

    @classmethod
    def get_or_create(cls, func: Callable, default=None):
        """Get an existing endpoint. If the endpoint does not exist it will be created

        Args:
            func: The callable for which we want to retrieve this ArgTyper attribute
            default: The default value to set this attribute to, in case it can't be found and needs to be created.
                If set do `None` (default), an instance of the class will be created. Otherwise, default will be used.
        """
        existing = cls.get(func)
        if existing:
            return existing
        func = cls._get_unbound_function(func)
        if not default:
            cls()(func)
        else:
            cls._registered_functions[func] = default
        return cls._registered_functions[func]

    @classmethod
    def _get_all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c._get_all_subclasses()]
        )

    @classmethod
    def has_attribute(cls, func: Callable) -> bool:
        """ Check if a Callable has any ArgTyper attribute set """
        subs = cls._get_all_subclasses()
        for c in subs:
            if c.get(func):
                return True
        return False

    @abstractmethod
    def __call__(self, func: Callable):
        ...

    def get_set_options(self, ignore=None) -> Dict:
        """ Returns the arg_options that do not have the default value set """
        ignore = ignore or []
        return {
            k: v
            for k, v in self.arg_options.items()
            if not isinstance(v, DEFAULT) and k not in ignore
        }


class Argument(ArgTyperAttribute):
    """Set options for a specific attribute

    This allows one to set additional information or change default values created by ArgTyper for a function parameter.
    This works similar to the options you can pass to argparsers ``add_argument``. There are two main differences here:

    1. The first parameter (`reference`) is the name of the function parameter
       for which you want to change the default options
    2. The next parameter (`name_or_flags`) is required for `add_argument`,
       but will default to the parameters name if left blank here.
    3. The rest of the parameters can be used to override values created automatically by
       ArgTyper or add additional information (like `description` or `help` text)

    Args:
        reference: The name of the function parameter that we want to change the options for
        name_or_flags: The alternate names or flags we want to use for this parameter
    """

    _registered_functions: Dict = dict()

    def __init__(
        self,
        reference,
        *name_or_flags: Text,
        action: Union[Text, Type[Action], DEFAULT] = Default,
        nargs: Union[int, Text, DEFAULT] = Default,
        const: Any = Default,
        default: Any = Default,
        type: Union[
            Callable[[Text], _T], Callable[[str], _T], FileType, DEFAULT
        ] = Default,
        choices: Union[Iterable[_T], DEFAULT] = Default,
        required: Union[bool, DEFAULT] = Default,
        help: Optional[Union[Text, DEFAULT]] = Default,
        metavar: Optional[Union[Text, Tuple[Text, ...], DEFAULT]] = Default,
        dest: Optional[Union[Text, DEFAULT]] = Default,
        version: Union[Text, DEFAULT] = Default,
        **kwargs: Any,
    ):

        self.reference = reference
        self.arg_names = name_or_flags
        self.arg_options: Dict[str, Any] = dict()
        self.arg_options["action"] = action
        self.arg_options["nargs"] = nargs
        self.arg_options["const"] = const
        self.arg_options["default"] = default
        self.arg_options["type"] = type
        self.arg_options["choices"] = choices
        self.arg_options["required"] = required
        self.arg_options["help"] = help
        self.arg_options["metavar"] = metavar
        self.arg_options["dest"] = dest
        self.arg_options["version"] = version
        self.kwargs = kwargs

    def __call__(self, func: Callable) -> Callable:
        options = self._registered_functions.setdefault(func, {})
        if self.reference in options:
            raise ArgTyperArgumentException(
                func, self.reference, f"Option for parameter was defined more than once"
            )

        options[self.reference] = self
        return func


class Command(ArgTyperAttribute):
    """Command object to hold information on ArgTyper commands

    The attributes are either used to instantiate an ``argparser.ArgumentParser`` instance or
    are passed to ``subparsers.add_parser()`` in case this command is a subcommand of another command.
    Look for a description in the official documentation of argparser.
    The argument `help` will only take effect for subcommands.

    The remaining arguments described here are used for ArgTyper configuration.

    Args:
        ignore_args: List of parameter names to be ignored when creating the argument parser
        ignore_types: List of types to be ignored when creating the argument parser.
        harcoded_names: Mapping of `argname:values` to be used as argument for parameters with those names
            This will always have precedence and overwrite anything else that might have been passed.
            Use `arg_defaults` in case this is not the behaviour you want. It also Takes precedence over `hardcode_types`
        hardcoded_types: Mapping of `<types>:values` to be used as argument for parameters with those types.
            This will always overwrite parameters with this type and ignore things set in arg_defaults.
        arg_defaults: Mapping of Parameter names to default values. This will be passed to `argparse.ArgumentParser.set_defaults`
    """

    _registered_functions: Dict = dict()

    def __init__(
        self,
        *,
        ignore_args: List[str] = None,
        ignore_types: List = None,
        hardcoded_names: Dict[str, Any] = None,
        hardcoded_types: Dict[Any, Any] = None,
        arg_defaults: Dict[str, Any] = None,
        prog=Default,
        usage=Default,
        description=Default,
        epilog=Default,
        parents=Default,
        formatter_class=Default,
        prefix_chars=Default,
        fromfile_prefix_chars=Default,
        argument_default=Default,
        conflict_handler=Default,
        add_help=Default,
        allow_abbrev=Default,
        exit_on_error=Default,
        help=Default,  # Only used when the command is added as subcommand
    ):

        # Argparse attributes
        if prog == None:
            prog = sys.argv[0]

        self.arg_options: Dict[str, Any] = dict()
        self.arg_options["prog"] = prog
        self.arg_options["usage"] = usage
        self.arg_options["description"] = description
        self.arg_options["epilog"] = epilog
        self.arg_options["parents"] = parents or []
        self.arg_options["prefix_chars"] = prefix_chars
        self.arg_options["formatter_class"] = formatter_class
        self.arg_options["fromfile_prefix_chars"] = fromfile_prefix_chars
        self.arg_options["argument_default"] = argument_default
        self.arg_options["conflict_handler"] = conflict_handler
        self.arg_options["add_help"] = add_help
        self.arg_options["allow_abbrev"] = allow_abbrev
        self.arg_options["exit_on_error"] = exit_on_error
        self.arg_options["help"] = help

        # Internal attributes
        self.ignore_args = ignore_args or []
        self.ignore_types = ignore_types or []
        self.arg_defaults = arg_defaults or {}
        self.hardcoded_names = hardcoded_names or {}
        self.hardcoded_types = hardcoded_types or {}
        self.handled_args: List[str] = []
        self.hardcoded_args: Dict[str, Any] = {}

    def get_argparser(self):
        options = self.get_set_options(ignore=["help"])
        parser = ArgParser(**options)
        return parser

    def set_as_subparser(self, subparsers, command_name=None) -> ArgumentParser:
        command_name = command_name or self.arg_options["prog"]
        options = self.get_set_options()
        options["prog"] = command_name
        parser = subparsers.add_parser(command_name, **options)

        return parser

    def __call__(self, func: Callable) -> Callable:
        if self.get(func):
            raise ArgTyperArgumentException(
                f"Can only set Command once for function '{func.__qualname__}'. Tried to set more than once"
            )
        self.get_or_create(func, default=self)
        return func


class SubParser(ArgTyperAttribute):
    """Add additional info to the subparser instance, in case the command has subcommands.

    This information is passed to ``ArgumentParser.add_subparsers``
    """

    _registered_functions: Dict = dict()

    def __init__(
        self,
        *,
        title=Default,
        description=Default,
        prog=Default,
        parser_class=Default,
        action=Default,
        option_sring=Default,
        dest=Default,
        required=Default,
        help=Default,
        metavar=Default,
    ):

        self.arg_options: Dict[str, Any] = dict()
        self.arg_options["title"] = title
        self.arg_options["description"] = description
        self.arg_options["prog"] = prog
        self.arg_options["parser_class"] = parser_class
        self.arg_options["action"] = action
        self.arg_options["option_sring"] = option_sring
        self.arg_options["dest"] = dest
        self.arg_options["required"] = required
        self.arg_options["help"] = help
        self.arg_options["metavar"] = metavar

    def __call__(self, func: Callable) -> Callable:
        if self.get(func):
            raise ArgTyperArgumentException(
                f"Can only set SubParser once for function '{func.__qualname__}'. Tried to set more than once"
            )
        self.get_or_create(func, default=self)
        return func

    def add_subparser_to_parser(self, parser: ArgumentParser) -> Action:
        subparsers = parser.add_subparsers(**self.get_set_options())
        return subparsers


class SubCommand(ArgTyperAttribute):
    """Add a subcommand to this ArgTyper command

    When calling subcommands, all predecessors will be called with their respective arguments as well.

    Warning:
        There is no check in place if you have a circle in your subcommands. (e.g. sub1 -> sub2 -> sub1 -> ...).
        This can happen for example if you use 'strings' to resolve command names inside a class.
        But in that case you will get a ``RecursionError``

    Args:
        subfunction: the function to be used/called as subcommand. This can either be a
            Callable or string. Callables will be used 'as is'. For strings, the
            function will be resolved from innermost to outermost namespace. This can
            be used to e.g. reference other functions inside the same class to be used
            as subcommands
        name: Optionally, a name to be used for this subcommand
    """

    _registered_functions: Dict = dict()

    def __init__(self, subfunction: Union[Callable, Text], name: Optional[Text] = None):
        self.subfunction: Optional[Callable] = None
        if callable(subfunction):
            self.subfunction = subfunction
            self.subfunction_name = subfunction.__name__
        else:
            self.subfunction_name = subfunction

        self.name = name or self.subfunction_name

    def __call__(self, func: Callable) -> Callable:
        subcommands = self._registered_functions.setdefault(func, [])
        subcommands.append(self)
        return func

    def get_subfunction(self, namespace) -> Callable:
        if self.subfunction:
            return self.subfunction

        namespaces = [namespace]
        namespaces.append(getattr(namespace, "__self__", {}))
        namespaces.append(namespace.__globals__)
        namespaces.append(globals())

        for entry in namespaces:
            self.subfunction = self.subfunction or getattr(
                entry, self.subfunction_name, None
            )

        if not self.subfunction:
            self.subfunction

        if not self.subfunction:
            raise ArgTyperException(
                f"Can not resolve function name {self.subfunction_name} in current namespace f{namespace}"
            )
        return self.subfunction


class MutuallyExclusiveArgumentGroup(ArgTyperAttribute):
    """Add an argument group to this function

    Args:
        arguments: A list of function argument names to be placed in this group.
            This list should contain the "original" names, not the ones you might have set with Attribute.
            Arguments in a mutually exclusive group need to be optional arguments only
        required: Indicate if at least one of the arguments is required to be set or not (default: False)
    """

    _registered_functions: Dict = dict()

    def __init__(self, arguments: List[str], required=False):
        self.arguments = arguments
        self.required = required
        self.group = None

    def get_group(self, parser: ArgParser):
        if not self.group:
            self.group = parser.add_mutually_exclusive_group(required=self.required)
        return self.group

    def __call__(self, func: Callable) -> Callable:
        options = self._registered_functions.setdefault(func, [])
        options.append(self)
        return func


class ArgumentGroup(ArgTyperAttribute):
    """Add an argument group to this function

    Args:
        arguments: A list of function argument names to be placed in this group.
            This list should contain the "original" names, not the ones you might have set with Attribute
        title: Optionally, a title for this group
        description: Optionally, a description for this group
    """

    _registered_functions: Dict = dict()

    def __init__(self, arguments: List[str], title: str = None, description=None):
        self.arguments = arguments
        self.title = title
        self.description = description
        self.group = None

    def get_group(self, parser: ArgParser):
        if not self.group:
            self.group = parser.add_argument_group(self.title, self.description)
        return self.group

    def __call__(self, func: Callable) -> Callable:
        options = self._registered_functions.setdefault(func, [])
        options.append(self)
        return func
