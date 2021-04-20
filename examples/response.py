import argtyper


def subfunc():
    return "Just returning more"


@argtyper.SubCommand(subfunc)
async def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))
    return "We also return here"


at = argtyper.ArgTyper(hello)
responses = at(return_responses=True)

print(f"Responses: {responses}")
