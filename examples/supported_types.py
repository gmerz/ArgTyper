import argtyper
from pathlib import Path


def type_test(
    name,
    yesno: bool,
    flag: bool = False,
    f: Path = None,
):
    print(f"name:   {name}")
    print(f"yesno:  {yesno}")
    print(f"flag:   {flag}")
    print(f"f:      {f}")


at = argtyper.ArgTyper(type_test)
at()
