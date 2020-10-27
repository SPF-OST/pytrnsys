.. _config_file:

Configuration files
===================

Pytrnsys runs and processes TRNSYS simulations based on configuration files. The general idea behind this is to provide
a fast and easily accessible way to define, run and analyse both single simulations as well as parametric studies. There
are distinct configuration files for running and processing. Both are described in the subsequent sections but follow
the same syntax and format.

The configuration file does not require a header. It should contain different keyword commands on single lines.
Comments start with ``#`` characters. End of line comments are possbile.

The config file supports the following basic types:

==========================  ===================================
*bool*                      with True/False as possible value
*int*                       with any interger as possible value
*string*                    with any string as possible value
*stringArray*               array of strings
==========================  ===================================

Parameters that are used to specifiy the run can be defined by::

    keyword parameter_name value

In the case of an integer this would for example be::

    int reduceCpu  4

.. note::

   The ``string`` and ``stringArray`` always have to be specified with parentheses.