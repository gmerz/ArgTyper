import argtyper


class CustomArg(object):
    def __init__(self, string):
        self.data = string
        if "jedi" not in string.lower():
            raise ValueError("Error in custom Argument")

    def __str__(self):
        return f"Custom Argument({self.data})"


def type_test(
    pos_arg: CustomArg,
    opt_arg: CustomArg = None,
):
    print(f"Positional Arg: {pos_arg}")
    print(f"Optional Arg:   {opt_arg}")


at = argtyper.ArgTyper(type_test)
at()
