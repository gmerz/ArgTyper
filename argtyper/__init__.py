import argparse
import asyncio
import inspect
import os
import shlex
import sys
import typing
import uuid
from argparse import Action, ArgumentParser
from typing import Any, Callable, Dict, List, Optional, Text, Tuple, Union, cast

from .actions import BoolAction, TupleAction, TypedChoiceAction
from .base import (
    ArgParser,
    Argument,
    Command,
    SubCommand,
    SubParser,
    ArgumentGroup,
    MutuallyExclusiveArgumentGroup,
    remove_uuid4_prefix,
    change_metavar,
)
from .exceptions import (
    ArgParserException,
    ArgParserExitException,
    ArgTyperException,
    ArgTyperArgumentException,
)


class ArgTyper:
    """The main Argtyper class

    Argtyper is a wrapper to allow the creation of an argparser.ArgumentParser by using function type information
    and (optionally) decorators. You can either use it to parse command line arguments or strings into arguments for function calls

    Args:
        func: The function to call/wrap as entrypoint
        progname: Optional program name. If not set to `None`, only run this ArgTyper if the program name matches this parameter.
            This option only has an effect if the ArgTyper is used to parse command line arguments, and not if strings are parsed
        ignore_types: A List of types for those the parameters will be ignored when creating the parser for commands and subcommands
        ignore_args: List of argument names to ignore when creating the parser for commands and subcommands
        hardcoded_args: Mapping of ``argname:values`` to be used as argument for parameters with those names
        hardcoded_types: Mapping of ``<types>:values`` to be used as argument for parameters with those types
        arg_defaults: Mapping of Parameter names to default values. This will be passed to :py:class:`argparse.
                ArgumentParser.set_defaults()` after processing the defaults for the Command wrappers.
                So, this will always overwrite defaults set somewhere else.
        version: If provided, the ``--version`` and ``-v`` arguments will be added and will print the
                provided version string. ``%(prog)s`` can be used to reference the current program name
    """

    def __init__(
        self,
        func: Callable,
        progname: Optional[str] = None,
        ignore_types: List = None,
        ignore_args: List[str] = None,
        hardcoded_names: Dict[str, Any] = None,
        hardcoded_types: Dict[Any, Any] = None,
        arg_defaults: Dict[str, Any] = None,
        version: Optional[str] = None,
    ):
        self.command_function = func
        arg_command = Command.get_or_create(func)
        arg_command.arg_options["prog"] = (
            progname if progname != None else arg_command.arg_options["prog"]
        )
        self.parser = None
        self.remapped_parameters: Dict[str, str] = {}
        self.progname = progname
        self.subparser_level = 0
        self.ignore_args = ignore_args or []
        self.ignore_types = ignore_types or []
        self.hardcoded_names = hardcoded_names or {}
        self.hardcoded_types = hardcoded_types or {}
        self.arg_defaults = arg_defaults or {}
        self.version = version

    def _parse_parameter(
        self, name: str, param: inspect.Parameter, arg_command: Command, prefix: str
    ) -> Optional[Tuple[str, Dict]]:

        parser_options = dict()

        ignore_args = self.ignore_args + arg_command.ignore_args
        ignore_types = self.ignore_types + arg_command.ignore_types

        # Python >= 3.9
        hardcoded_names = self.hardcoded_names | arg_command.hardcoded_names
        hardcoded_types = self.hardcoded_types | arg_command.hardcoded_types

        origin_type = typing.get_origin(param.annotation)
        origin_args = typing.get_args(param.annotation)

        # *args or **kwargs
        if param.kind in [param.VAR_KEYWORD, param.VAR_POSITIONAL]:
            return None

        # positional only params are not supported
        if param.kind == param.POSITIONAL_ONLY:
            raise ArgTyperException(
                "'Positional only' arguments are currently not supported by argtyper"
            )

        if origin_type is None:
            origin_type = param.annotation

        origin_type = cast(Any, origin_type)

        if name in hardcoded_names:
            arg_command.hardcoded_args[name] = hardcoded_names[name]
            return None

        if origin_type in hardcoded_types:
            arg_command.hardcoded_args[name] = hardcoded_types[origin_type]
            return None

        # Ignore those parameter names
        if name in ignore_args:
            return None
        if param.annotation == param.empty:
            origin_type = str
        #            return None

        if origin_type in ignore_types:
            return None

        if param.default == param.empty:
            param_name = name
            parser_options["metavar"] = name
        else:
            if len(name) > 1:
                param_name = f"{prefix[0] * 2}{name}"
            else:
                param_name = f"{prefix[0] * 1}{name}"
            parser_options["default"] = param.default
            parser_options["metavar"] = name.upper()

        # Handle types
        if origin_type == list:
            parser_options["action"] = "extend"
            parser_options["nargs"] = "+"
            help_text = "provide a list"
            if len(origin_args) == 1:
                parser_options["type"] = origin_args[0]
                help_text += f" of {origin_args[0].__name__.upper()} values"
            parser_options["help"] = help_text

        elif origin_type == tuple:
            parser_options["action"] = TupleAction
            parser_options["nargs"] = len(origin_args)
            # The metavar behaves differently for positional arguments
            # if param.default != param.empty:
            parser_options["metavar"] = origin_args
        elif origin_type == bool:
            if param.default != param.empty:
                # store_true and store_false do not support metavar
                del parser_options["metavar"]
                if param.default is True:
                    parser_options["action"] = "store_false"
                    parser_options["help"] = "toggle option (default: True)"
                else:
                    parser_options["action"] = "store_true"
                    parser_options["help"] = "toggle option (default: False)"
            else:
                parser_options["action"] = BoolAction
        elif origin_type == typing.Literal:
            parser_options["choices"] = origin_args
            parser_options["action"] = TypedChoiceAction
        elif issubclass(origin_type, argparse.Action):
            parser_options["action"] = origin_type

        if "action" not in parser_options and "type" not in parser_options:
            parser_options["type"] = origin_type
            parser_options[
                "help"
            ] = f"provide argument of type {origin_type.__name__.upper()}"

        return param_name, parser_options

    def _get_param_defaults(self, func: Callable, name: str) -> Optional[Argument]:
        defaults = Argument.get(func)
        if defaults:
            return defaults.get(name, None)
        return None

    def _prepare_parameter(
        self,
        parser: Union[ArgParser, ArgumentParser],
        param_name: str,
        param: inspect.Parameter,
        func: Callable,
        arg_command: Command,
    ) -> Optional[Dict]:

        result = self._parse_parameter(
            param_name, param, arg_command, parser.prefix_chars
        )
        remapped_parameters: Dict[str, str] = {}

        if not result:
            return None

        unique_name = f"{uuid.uuid4().hex}_{param_name}"
        # arg_command.handled_args.append(name)
        arg_command.handled_args.append(unique_name)
        defaults = self._get_param_defaults(func, param_name)

        name, kwargs = result
        name_or_flags: Tuple[str, ...] = (name,)

        if defaults:
            if defaults.arg_names:

                remapped_parameters = {
                    k.lstrip(parser.prefix_chars): unique_name
                    for k in defaults.arg_names
                }

                name_or_flags = defaults.arg_names

            kwargs.update(defaults.get_set_options())
            kwargs.update(defaults.kwargs)

        if len(name_or_flags) > 1:
            change_metavar(kwargs, "upper")
            kwargs["dest"] = unique_name
        else:
            if name_or_flags[0].startswith(parser.prefix_chars[0]):
                kwargs["dest"] = unique_name
                change_metavar(kwargs, "upper")
            else:
                name_or_flags = (unique_name,)
                change_metavar(kwargs, "upper")

        arg_groups = ArgumentGroup.get(
            func, default=[]
        ) + MutuallyExclusiveArgumentGroup.get(func, default=[])
        in_group = False
        try:
            for arg_group in arg_groups:
                if param_name in arg_group.arguments:
                    group = arg_group.get_group(parser)
                    group.add_argument(*name_or_flags, **kwargs)
                    in_group = True
        except ValueError as e:
            raise ArgTyperArgumentException(func, name, str(e)) from e

        if not in_group:
            parser.add_argument(*name_or_flags, **kwargs)
        return remapped_parameters

    def _prepare_subcommands(
        self, func: Callable, parser: ArgumentParser, subcommand_level: int
    ) -> None:
        subcommands = SubCommand.get(func, default=[])
        subcommands = cast(List[SubCommand], subcommands)
        if not subcommands:
            return
        subparser_info = SubParser.get_or_create(func)
        subparsers = subparser_info.add_subparser_to_parser(parser)
        for subcommand in subcommands:
            subfunc = subcommand.get_subfunction(func)
            self._prepare_parser(subfunc, subparsers, subcommand.name, subcommand_level)

    def _prepare_parser(
        self,
        func: Callable,
        subparsers: Optional[Action] = None,
        subcommand_name: Optional[str] = None,
        subcommand_level: int = 0,
    ) -> None:
        if self.parser:
            return
        sig = inspect.Signature.from_callable(func)
        arg_command = Command.get_or_create(func)
        # arg_command = self._get_argtyper_command(func)
        if subparsers:
            parser = arg_command.set_as_subparser(subparsers, subcommand_name)
            parser.set_defaults(**arg_command.arg_defaults)
            function = {f"_argtyper_function_{subcommand_level}": func}
            parser.set_defaults(**function)
        else:
            parser = arg_command.get_argparser()
            parser.set_defaults(**arg_command.arg_defaults)

        parser.set_defaults(**self.arg_defaults)
        parser.prog = parser.prog if parser.prog != None else func.__name__

        remapped_parameters: Dict = dict()

        # Handle "parents=" arguments
        for act in parser._actions:
            arg_command.handled_args.append(act.dest)

        # TODO was there a reason this was here and hardcoded? Hmmm....
        # parser.allow_abbrev = False

        for name, param in sig.parameters.items():
            new_remapped_parameters = self._prepare_parameter(
                parser, name, param, func, arg_command
            )
            if new_remapped_parameters:
                remapped_parameters.update(new_remapped_parameters)
        self._prepare_subcommands(func, parser, subcommand_level + 1)
        self.remapped_parameters.update(remapped_parameters)

        if not subcommand_level:
            # parser.set_defaults(**self.arg_defaults)
            self.parser = parser
            if self.version:
                self.parser.add_argument(
                    "--version", "-v", action="version", version=self.version
                )

    def _parse_command(self, current_function: Callable, unhandled: Dict):
        """ Parse an argcommand and return the arguments handled by this command """
        arg_command = Command.get(current_function, raise_exc=True)

        handled_args = {
            remove_uuid4_prefix(k): v
            for k, v in unhandled.items()
            if k in arg_command.handled_args
        }
        handled_args = handled_args | arg_command.hardcoded_args
        unhandled = {
            k: v for k, v in unhandled.items() if k not in arg_command.handled_args
        }
        return handled_args, unhandled

    def _parse_subcommands(self, unhandled) -> List:
        """ Parse SubCommands for a Command """
        subfunctions = [
            int(x.removeprefix("_argtyper_function_"))
            for x in unhandled
            if x.startswith("_argtyper_function_")
        ]
        if not subfunctions:
            return []
        calls = []
        next_func_number = sorted(subfunctions)[0]
        current_function = unhandled.pop(f"_argtyper_function_{next_func_number}")

        handled, unhandled = self._parse_command(current_function, unhandled)
        calls.append((current_function, handled))

        sub_calls = self._parse_subcommands(unhandled)
        calls.extend(sub_calls)
        return calls

    def get_parser(self):
        """ Prepare and return the ArgumentParser instance """
        self._prepare_parser(self.command_function)
        return self.parser

    def get_function_calls(self, input_args) -> List[Tuple[Callable, Dict[str, Any]]]:
        """ Run the parser on the input and return a List with a mapping of (function , kwargs) for matches"""
        calls: List = []
        if not self.parser:
            raise ArgTyperException("Parser not set up. This should not happen here")
        args = self.parser.parse_args(input_args)
        # Remap arguments
        for arg in list(args.__dict__.keys()):
            if arg in self.remapped_parameters:
                setattr(args, self.remapped_parameters[arg], getattr(args, arg))
                delattr(args, arg)

        handled, unhandled = self._parse_command(self.command_function, vars(args))
        calls.append((self.command_function, handled))
        sub_calls = self._parse_subcommands(unhandled)
        calls.extend(sub_calls)
        return calls

    def call_parser_sync(self, input_args: List[str]) -> List:
        """ Run the parser on the input arguments and execute the corresponding functions """
        self._prepare_parser(self.command_function)

        responses = []
        calls = self.get_function_calls(input_args)

        for func, kwargs in calls:
            if inspect.iscoroutinefunction(func):
                response = asyncio.run(func(**kwargs))
            else:
                response = func(**kwargs)
            responses.append(response)
        return responses

    async def call_parser_async(self, input_args: List[str]) -> List:
        """ Run the parser on the input arguments and execute the corresponding functions """
        self._prepare_parser(self.command_function)

        responses: List = []
        calls = self.get_function_calls(input_args)

        for func, kwargs in calls:
            if inspect.iscoroutinefunction(func):
                response = await func(**kwargs)
            else:
                response = await asyncio.to_thread(func, **kwargs)
            responses.append(response)
        return responses

    def _call_interactive(self, return_responses=False):
        """ Call with command line arguments """
        exit_status = 0
        try:
            # We don't call the parser if the progname does not match
            if self.progname and self.progname != os.path.basename(sys.argv[0]):
                return
            input_args = sys.argv[1:]
            responses = self.call_parser_sync(input_args)
            if return_responses:
                return responses
        except ArgParserException as exc:
            print(self.parser.format_usage(), file=sys.stderr)
            exit_status = 1
            print("Error:", exc, file=sys.stderr)
        except ArgParserExitException as exc:
            print(exc.parser._message)
            exit_status = exc.status
        else:
            if getattr(self.parser, "_message", None):
                print(self.parser._message)

        sys.exit(exit_status)

    def _call_inline(self, message) -> List:
        """ Call with a string """
        input_args = shlex.split(message)
        return self.call_parser_sync(input_args)

    def __call__(
        self, message: Optional[Text] = None, return_responses=False
    ) -> Optional[List]:
        """Run the Argtyper, parse arguments and call functions

        Args:
            message: If message is set to a string, this string will be parsed into arguments. If set to None, command line arguments will be used.
        """

        if message:
            return self._call_inline(message)
        return self._call_interactive(return_responses)
