import argtyper

def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))

at = argtyper.ArgTyper(hello)

parser = at.get_parser()
parser.add_argument('--myversion', action='version', version="Super %(prog)s 1.3.3.7")

at()
