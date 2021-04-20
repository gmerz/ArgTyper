import argtyper
from typing import Tuple


def type_test(
    pos_arg: Tuple[int, float],
    opt_arg: Tuple[str, int, str] = ("Nr.", 1, "Tester"),
):
    print(f"Positional Arg: {pos_arg}")
    print(f"Optional Arg:   {opt_arg}")


at = argtyper.ArgTyper(type_test)
at()
