Supported Type Annotations
==========================

The following gives a short overview on (known) supporte type hints for ArgTyper.
Since ArgTyper internally tries to convert type annotions to their base types, there might be more.

.. warning:: Be ware that default values are never verified and can be arbitrarily set.


Standard Types
--------------

.. literalinclude:: ../../examples/supported_types.py

This would produce the following output for the parser:

.. include:: examples/help/supported_types_help.rst

.. include:: examples/run/supported_types_success_1.rst

.. include:: examples/run/supported_types_success_2.rst

.. include:: examples/run/supported_types_success_3.rst

.. include:: examples/run/supported_types_fail_1.rst



Lists
-----

.. literalinclude:: ../../examples/type_list.py

This would produce the following output for the parser:

.. include:: examples/help/type_list_help.rst

.. include:: examples/run/type_list_success_1.rst

.. include:: examples/run/type_list_success_2.rst

.. include:: examples/run/type_list_fail_1.rst


Tuples
------

.. literalinclude:: ../../examples/type_tuple.py

This would produce the following output for the parser:

.. include:: examples/help/type_tuple_help.rst

.. include:: examples/run/type_tuple_success_1.rst

.. include:: examples/run/type_tuple_success_2.rst

.. include:: examples/run/type_tuple_fail_1.rst


Literals
--------

.. literalinclude:: ../../examples/type_literal.py

This would produce the following output for the parser:

.. include:: examples/help/type_literal_help.rst

.. include:: examples/run/type_literal_success_1.rst

.. include:: examples/run/type_literal_success_2.rst

.. include:: examples/run/type_literal_fail_1.rst

.. include:: examples/run/type_literal_fail_2.rst


Custom Arguments 
----------------

You can create arbitrary arguments. The will receive the command line argument value
as ``string`` in the class' ``__init__`` function. For example, you can use this
for custom verification of arguments. You only need to raise an Exception to 
provoke a parsing error and exit.

.. literalinclude:: ../../examples/type_custom_arg.py

This would produce the following output for the parser:

.. include:: examples/help/type_custom_arg_help.rst

A successful execution would look like this:

.. include:: examples/run/type_custom_arg_success_1.rst

A failed execution, which throws an error, would look like this:

.. include:: examples/run/type_custom_arg_fail_1.rst


Custom Actions
----------------

Custom actions are more powerful, as they have more control during creation of the parser
and also during handling of arguments. CustomActions are subclasses of :py:class:`argparse.Action`.

.. literalinclude:: ../../examples/type_custom_action.py

This would produce the following output for the parser:

.. include:: examples/help/type_custom_action_help.rst

And if run, we can see that :py:func:`CustomAction.__call__` is executed during parsing, and before 
execution is handed over from the parser to the actual function ``type_test``.

.. include:: examples/run/type_custom_action_success_1.rst

Another thing that can be seen here are the argument names in the namespace. Internally, ArgTyper prefixes
destinations with a random uuid4 value, to prevent argument name collisions in parent and child functions.

The only places where you should come into contact with that are either if you implement custom actions,
or if you use the parser instance directly yourself. For both cases you can use :py:func:`argtyper.base.remove_uuid4_prefix(<string>)`
to remove the prefix and retrieve the correct argument names from ``dest``.
