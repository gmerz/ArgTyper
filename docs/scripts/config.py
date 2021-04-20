from collections import defaultdict
from pathlib import Path


script_dir = Path(__file__).parent

example_dir = script_dir / '..' / '..' / 'examples'
doc_dir = script_dir / '..' / 'source' / 'examples'


commands = defaultdict(dict)

# A Mapping of python example file names to a mapping of "file_suffix" : "command line arguments" 
# for inclusion in the documentation

commands['simple'] = dict(
        success_1 = 'Yoda',
        success_2 = 'Yoda --amount 4',
        fail_1 = 'Yoda --amount z'
        )

commands['response'] = dict(
        success_1 = 'Yoda',
        success_2 = 'Yoda subfunc'
        )

commands['wrap_external'] = dict(
        success_1 = "'needle' 'searching for needle in a haystack'",
        )

commands['exclusive_group'] = dict(
        fail_1 = "supernick --foo FOO --bar BAR",
        )

commands['parents'] = dict(
        success_1 = "'My Signature' 'the footer' --hide --show",
        )

commands['class_method'] = dict(
        success_1 = "test_message 'An important message'",
        fail_1 = "get_value",
        fail_2 = "get_value something"
        )

commands['supported_types'] = dict(
        success_1 = "'Han Solo' 1",
        success_2 = "'Han Solo' false --flag",
        success_3 = "'Han Solo' false --flag -f somepath",
        fail_1 = "'Han Solo' foo",
        )

commands['type_custom_arg'] = dict(
        success_1 = "jedi",
        fail_1 = "sith")

commands['type_custom_action'] = dict(
        success_1 = "'custom action input'")

commands['type_list'] = dict(
        success_1 = "1 a b",
        success_2 = "1 a b --opt_arg 1 2 3 4",
        fail_1 = "1 a b --opt_arg z 1")

commands['type_tuple'] = dict(
        success_1 = "1 0.03",
        success_2 = "1 0.03 --opt_arg more 2 see",
        fail_1 = "1 z")

commands['type_literal'] = dict(
        success_1 = "yes",
        success_2 = "no --opt_arg more 2 see",
        fail_1 = "1 ",
        fail_2 = "yes --opt_arg 30")

