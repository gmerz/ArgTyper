import argtyper


class Test:
    def __init__(self, value):
        self.value = value

    def test_message(self, message: str):
        print(message)
        print(self.value)

    def get_value(self):
        print(self.value)

    @argtyper.SubCommand(get_value)
    @argtyper.SubCommand("test_message")
    def entry(
        self,
    ):
        ...


t = Test("---- Instance Value ----")
at = argtyper.ArgTyper(t.entry)
at()
