import argtyper
from typing import Literal


def type_test(
    pos_arg: Literal["yes", "no"], opt_arg: Literal["true", "false", 10, 20] = 30
):
    print(f"Positional Arg: {pos_arg}, {type(pos_arg)}")
    print(f"Optional Arg:   {opt_arg}, {type(opt_arg)}")


at = argtyper.ArgTyper(type_test)
at()
