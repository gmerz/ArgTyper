import argtyper
from typing import List


def type_test(
    pos_arg: List,
    opt_arg: List[int] = None,
):
    print(f"Positional Arg: {pos_arg}")
    print(f"Optional Arg:   {opt_arg}")


at = argtyper.ArgTyper(type_test)
at()
