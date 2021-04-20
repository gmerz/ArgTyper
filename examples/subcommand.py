import argtyper


def footer1(footer: str, hide: bool = False):
    if not hide:
        print(f"-- {footer}")


async def footer2(footer: str, repeat: int = 2):
    print(f"{footer}" * repeat)


# Subcommands are `registered` at the parent
@argtyper.SubCommand(footer1, name="footer_main")
@argtyper.SubCommand(footer2)
def hello(name: str, amount: int = 5):
    print(f"Hello {name.upper()}\n" * amount)


at = argtyper.ArgTyper(hello, arg_defaults={"amount": 2})
at()
