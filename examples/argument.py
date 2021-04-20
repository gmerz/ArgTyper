import argtyper


@argtyper.Argument(
    "amount", "repetitions", help="How often should we say hello?", metavar="reps"
)
@argtyper.Argument("name", "--name", "--n", help="Give me your name", default="Yoda")
def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))


at = argtyper.ArgTyper(hello, version="This is %(prog)s version 1.3.3.7")
at()
