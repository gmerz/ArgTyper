Additional Features
===================

ArgTyper provides some additional features, which might be useful in specific circumstances.


Responses
---------

Internally, ArgTyper handles execution of all functions and subfunctions for you. However, sometimes you might need to work with the results from those function calls.
For this purpose, ArgTyper allows you to return a List containing the results returned by the respective function calls (by setting ``return_response=True``).

.. literalinclude:: ../../examples/response.py

This will produce the following output for the parser.

.. include:: examples/help/response_help.rst

As can be seen, the response are not printed, since the parser prints the help message and exits. 
Same happens if the parser would encounter an error during argument parsing.
On the other hand, a successfull run would produce this output.

.. include:: examples/run/response_success_1.rst

Calling subcommands will add more entries to the list of returned values:

.. include:: examples/run/response_success_2.rst


Wrapping external methods
-------------------------

Since decorators can also be used as normal functions, and the way ArgTyper is built,
it is also quite easy to wrap external/included functions.

.. literalinclude:: ../../examples/wrap_external.py

This will produce the following output for the parser.

.. include:: examples/help/wrap_external_help.rst

And a successfull run would produce this output.

.. include:: examples/run/wrap_external_success_1.rst



Subcommands & Instance Methods
------------------------------

When working with classes, registering subcommands does not work exactly the same as for
other functions. The problem is, that the functions need to be bound to the correct
instances during runtime, in order for `self` to work correctly.

To support this use case, the argument provided to :class:`argtyper.SubCommand` to reference
a function can not only be passed as Callable, but also as string.
The following example will illustrate the difference between the two options.

.. literalinclude:: ../../examples/class_method.py

The first subcommand simply adds the function ``get_value``, while the second one uses the string ``test_message``
to add a subcommand. At first, there won't be any difference between the two for the help output:

.. include:: examples/help/class_method_help.rst

But the difference becomes apparent as soon as you try to call subcommands.
While ``test_command`` will work as expected:

.. include:: examples/run/class_method_success_1.rst

``get_value``, which should not take any parameters, will fail because it is missing an argument ``self``:

.. include:: examples/run/class_method_fail_1.rst

To further illustrate the issue, if we actually pass a value to ``self``, execution will fail with an error:

.. include:: examples/run/class_method_fail_2.rst

This issues exists, because if we add the function during class creation, we are not adding the bound instance method,
and therefore we can't access ``self`` during runtime.
However, if the argument is passed as string, ArgTyper will resolve the name during runtime and can therefore reference the 
correct instance method and execute the function correctly.


Parents=
--------

ArgumentParser also supports a `parent=` keyword to add arguments from another parser.
This is also (somewhat) supported in ArgTyper. For example, if you check the following program:

.. literalinclude:: ../../examples/parents.py

The commands will add the arguments of function ``sub1`` to function ``sub2``. And then those will be added
to function ``hello``. Then, if we call help, we can see that the arguments are added to the parser as expected.

.. include:: examples/help/parents_help.rst

To actually be able to handle additional arguments, we can simply use ``**kwargs`` inside ``hello``, which will then hold the values
for the parsed additional arguments.

.. include:: examples/run/parents_success_1.rst

Extend the Parser
-----------------

ArgTyper also gives you access to the underlying parser, in case you want to extend it.

.. literalinclude:: ../../examples/extend_parser.py

This will give you the following output.

.. include:: examples/help/extend_parser_help.rst
