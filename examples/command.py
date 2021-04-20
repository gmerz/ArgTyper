import argtyper


@argtyper.Command(
    description="Having a better description can improve your CLIs",
    epilog="And some more text at the end",
)
def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))


at = argtyper.ArgTyper(hello)
at()
