Basic Usage
===========

By itself, ArgTyper will only create parsers with very basic additional information on arguments.
To enhance the generated output and extend functionality, ArgTyper provides a set of decorators.
The following examples provide an overview of some of the features of ArgTyper.

Command
--------

The :class:`argtyper.Command` decorator can be used to pass additional arguments to the created ArgumentParser instance:


.. literalinclude:: ../../examples/command.py

This will produce the following output for the parser.

.. include:: examples/help/command_help.rst

It takes the same arguments that you can pass to `argparse.ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_.
You can also pass ``help`` as argument, which will be used if the command is used in a subparser.


Additionally, Command also gives you the ability to exclude arguments from the generated parser, set default values or hardcode the values for certain 
argument names or types. A description of the corresponding arguments can be found in the class description.



Argument
--------


The :class:`argtyper.Argument` decorator can be used to pass additional arguments to ``parser.add_argument()``
It takes the same arguments that you can pass to `argparse.ArgumentParser.add_argument <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument>`_. The main difference is that the first argument here is the name of the function argument to annotate.

.. literalinclude:: ../../examples/argument.py

This will produce the following output for the parser.

.. include:: examples/help/argument_help.rst

   
In this example we changed settings for the arguments ``amount`` and ``name``. This way we added more information to the help output.
But additionally, we are also able to change the underlying parser.

In this case, we changed the optional argument ``amount`` to a required argument with the new name ``reps``. The important thing here
is the argument ``repetitions``, which does not include the optional argument prefix ``-``. Therefore it will be interpreted as required.

Conversely, we changed the argument ``name`` to an optional argument by using names which are prefixed with a ``-``. Additionally we set a default value
(*Yoda*) to be passed to name, in case the argument is not passed on the command line.



SubCommand
----------

The :class:`argtyper.SubCommand` decorator can be used to create additional subparsers.
This is merely a helper function which does not have any direct counterpart in `argparse`.
It does, however, reuse information attached with argtyper.Command to subfunctions functions.

.. literalinclude:: ../../examples/subcommand.py

This will produce the following output for the parser.

.. include:: examples/help/subcommand_help.rst

SubCommand simply takes two arguments. The first one is the function (either Callable or name:str), the second one is an optional alternative name to be used for this subcommand.


SubParser
---------

The :class:`argtyper.SubParser` decorator can be used to add additional information to the
created subparsers instance. It is basically a wrapper around `argparse.ArgumentParser.add_subparsers <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers>`_ and takes the same arguments.

.. literalinclude:: ../../examples/subparser.py

This will produce the following output for the parser.

.. include:: examples/help/subparser_help.rst

The subcommands have now been grouped into their own sections with their own description.


ArgumentGroup
-------------

The :class:`argtyper.ArgumentGroup` decorator can be used to add argument groups to the parser.
It takes a list or argument names (as they appear in the function definition) and wraps them with 
`argparse.ArgumentParser.add_argument_group <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group>`_
during parser creation.

.. literalinclude:: ../../examples/argument_group.py

This will produce the following output for the parser.

.. include:: examples/help/argument_group_help.rst

The arguments have now been grouped into their own sections with their own description.

.. warning:: There is no check if you put the same argument into different groups. They might then appear more than once on the command line.


MutuallyExclusiveArgumentGroup
------------------------------

The :class:`argtyper.MutuallyExclusiveArgumentGroup` decorator can be used to add mutually exclusive argument groups to the parser.
This wraps `argparse.ArgumentParser.add_mutually_exclusive_group <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_mutually_exclusive_group>`_.

.. literalinclude:: ../../examples/exclusive_group.py

This will produce the following output for the parser.

.. include:: examples/help/exclusive_group_help.rst

The arguments have now been grouped into their own sections with their own description.

But now the parser will also make sure that at most one (or exactly one, if ``required=True``) of the arguments in the group is set.

.. include:: examples/run/exclusive_group_fail_1.rst


Conclusion
----------

While all decorators have been presented mostly on their own, they can of course also be combined at will.

