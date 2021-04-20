import argtyper


@argtyper.ArgumentGroup(
    ["firstname", "lastname"],
    title="Name details",
    description="Give your full name here",
)
@argtyper.ArgumentGroup(
    ["nickname", "firstname"],
    title="Nickname details",
    description="Give your Nickname here",
)
@argtyper.Argument(
    "amount", "repetitions", help="How often should we say hello?", metavar="reps"
)
@argtyper.Argument(
    "lastname", "--name", "--n", help="Give me your name", default="Yoda"
)
def hello(nickname: str, firstname: str, lastname: str, amount: int = 2):
    print("\n".join([f"Hello {firstname} '{nickname.upper()}' {lastname}"] * amount))


at = argtyper.ArgTyper(hello)
at()
