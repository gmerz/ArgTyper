import argtyper


@argtyper.MutuallyExclusiveArgumentGroup(["foo", "bar"], required=True)
def hello(nickname: str, foo: str = None, bar: str = None):
    print(locals())
    if foo:
        print(f"{nickname} + {foo}")
    else:
        print(f"{bar} + {nickname}")


at = argtyper.ArgTyper(hello)
at()
