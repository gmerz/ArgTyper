from argtyper.base import remove_uuid4_prefix
import argtyper
import argparse


class CustomAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        if "help" not in kwargs:
            kwargs["help"] = f"This is a custom action"
        super(CustomAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print("Parsing custom action: %r %r %r" % (namespace, values, option_string))
        setattr(namespace, self.dest, values)
        print(f"Argument Name: {argtyper.base.remove_uuid4_prefix(self.dest)}")
        print("------\nAction parsing finished\n-----\n")


def type_test(
    pos_arg: CustomAction,
    opt_arg: CustomAction = None,
):
    print(f"Positional Arg: {pos_arg}")
    print(f"Optional Arg:   {opt_arg}")


at = argtyper.ArgTyper(type_test)
at()
