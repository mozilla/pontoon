
.. _option_filteraction:

--filteraction=ACTION
*********************

.. _option_filteraction#none_default:

none (default)
==============

Take no action.  Messages from failing test will appear in the output file

.. _option_filteraction#warn:

warn
====

Print a warning but otherwise include the message in the output file.

.. _option_filteraction#exclude-serious:

exclude-serious
===============

Only exclude errors that are listed as serious by the convertor.  All other are
included.

.. _option_filteraction#exclude-all:

exclude-all
===========

Exclude any message that fails a test.
