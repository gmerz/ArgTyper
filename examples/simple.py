import argtyper


async def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))


at = argtyper.ArgTyper(hello)
at()
