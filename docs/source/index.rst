.. ArgTyper documentation master file, created by
   sphinx-quickstart on Mon Apr 12 14:20:28 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ArgTyper
========

**-- ArgumentParser on Typehints and Decorators**

ArgTyper provides and overlay for `argparse.ArgumentParser <https://docs.python.org/3/library/argparse.html#argumentparser-objects>`_ to create parsers
based on function type hint information enhanced with information provided by function decorators.

Additionally argtyper supports handling of async coroutines as well as normal functions.

Quickstart
----------

In it's simplest form, usage of ArgTyper looks as follows:

.. literalinclude:: ../../examples/simple.py

Assuming the Python code above is saved into a file called ``simple.py``, it can
be run at the command line and provides useful help messages:

.. include:: examples/help/simple_help.rst

When run with the appropriate arguments it looks like the following:


.. include:: examples/run/simple_success_1.rst

.. include:: examples/run/simple_success_2.rst

If invalid arguments are passed in, it will issue an error:

.. include:: examples/run/simple_fail_1.rst

For a more in-depth look on what ArgTyper can do for you, take a look at the following chapters.

.. toctree::
   :maxdepth: 2
   :caption: Introduction

   /basic_usage
   /advanced_usage
   /supported_types


Known Limitations
-----------------

+ custom `argparse.Actions` do not support `async` mode.  If you use custom actions while calling the parser in 
  `async` mode, those can potentially block the event loop for other tasks. 
  This shouldn't be a problem if they are not performing any I/O bound operations, though.


.. toctree::
   :maxdepth: 2
   :caption: Module Objects

   /module


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
