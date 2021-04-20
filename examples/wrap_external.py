import re
import argtyper

argtyper.Argument("pattern", help="The pattern to search for")(re.search)
argtyper.Argument(
    "string", help="The string, in which you want to search for the pattern"
)(re.search)
at = argtyper.ArgTyper(re.search)

responses = at(return_responses=True)
print(responses[0])
