import argtyper
import argparse


async def sub1(signature: str, hide: bool = False):
    if not hide:
        print(f"-- {signature}")


@argtyper.Command(parents=[argtyper.ArgTyper(sub1).get_parser()], add_help=False)
async def sub2(
    footer: str, debug: bool = False, show: argparse.BooleanOptionalAction = True
):
    print(footer, debug, show)


@argtyper.Command(parents=[argtyper.ArgTyper(sub2).get_parser()], add_help=False)
def hello(**kwargs):
    print("Hello", kwargs)


at = argtyper.ArgTyper(hello, arg_defaults={"amount": 2})
at()
