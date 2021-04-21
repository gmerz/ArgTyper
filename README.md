# ArgTyper

**-- ArgumentParser on Typehints and Decorators**

**Documentation:** https://argtyper.readthedocs.io/

**Source Code:** https://github.com/gmerz/ArgTyper

---

ArgTyper let's you build command line applications from python functions. Based on Python type hints and decorators.

**Features:**
+ Easy to get started
+ Supports and extends on the features provided by ArgumentParser
+ Wrap arbitrary functions. You can also easily work with imported functions. No need to change the original, if you don't want to.

## Requirements

Python 3.9+

**ArgTyper** does not have any external dependencies

## Installation

```console
pip install argtyper
```

## Example

### Getting started

In it’s simplest form, usage of ArgTyper looks as follows:

```python
import argtyper

async def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))

at = argtyper.ArgTyper(hello)
at()
```

Assuming the Python code above is saved into a file called `simple.py`, it can be run at the command line and provides useful help messages:

```console
$ python simple.py -h
usage: simple.py [-h] [--amount AMOUNT] NAME

positional arguments:
  NAME             provide argument of type STR

optional arguments:
  -h, --help       show this help message and exit
  --amount AMOUNT  provide argument of type INT
```

When run with the appropriate arguments it looks like the following:

```console
$ python simple.py Yoda
Hello YODA
Hello YODA

$ python simple.py Yoda --amount 4
Hello YODA
Hello YODA
Hello YODA
Hello YODA
```

If invalid arguments are passed in, it will issue an error:

```console
python simple.py Yoda --amount z
usage: simple.py [-h] [--amount AMOUNT] NAME

Error: simple.py: argument --amount: invalid int value: 'z'
```

### Extending the parser

Of course you can also customize the output and fit it to your needs. This is done 
with decorators. An example of how to change information for arguments take a look at the 
following example:

```python
import argtyper

@argtyper.Argument(
    "amount", "repetitions", help="How often should we say hello?", metavar="reps"
)
@argtyper.Argument("name", "--name", "--n", help="Give me your name", default="Yoda")
def hello(name: str, amount: int = 2):
    print("\n".join([f"Hello {name.upper()}"] * amount))

at = argtyper.ArgTyper(hello, version="This is %(prog)s version 1.3.3.7")
at()
```

This will produce the following output for the parser.

```console
$ python argument.py -h
usage: argument.py [-h] [--name NAME] [--version] REPS

positional arguments:
  REPS                  How often should we say hello?

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, --n NAME
                        Give me your name
  --version, -v         show program's version number and exit
```

In this example we changed settings for the arguments `amount` and `name`. This way we added more information to the help output. But additionally, we are also able to change the underlying parser.

In this case, we changed the optional argument `amount` to a required argument with the new name `reps`. The important thing here is the argument `repetitions`, which does not include the optional argument prefix `-`. Therefore it will be interpreted as required.

Conversely, we changed the argument `name` to an optional argument by using names which are prefixed with a `-`. Additionally we set a default value (Yoda) to be passed to name, in case the argument is not passed on the command line.

### Further extensions

ArgTyper also supports other functionality provided by ArgumentParser. Therefore it is also possible to implement Subcommands, ArgumentGroups or extend parsing of command line parameter with custom Actions.

For a more in-depth look of what ArgTyper can do for you, please refer to the [documentation](https://argtyper.readthedocs.io/)

## Similar tools

It is similar to [Typer](https://github.com/tiangolo/typer) (which has more
features), Contrary to Typer, which is based on [click](https://click.palletsprojects.com/en/7.x/),
ArgTyper is based on standard argparse.ArgumentParser (for better or for
worse).



