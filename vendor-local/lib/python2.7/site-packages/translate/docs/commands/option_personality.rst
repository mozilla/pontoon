
.. _option_personality:

--personality=TYPE
******************

.. _option_personality#java_default:

java (default)
==============

Create output strictly according to the specification for .properties files.
This will use escaped Unicode for any non-ASCII characters.  Thus the following
string found in a PO file::

  ṽḁḽṻḝ

Will appear as follows in the output .properties file::

  \u1E7D\u1E01\u1E3D\u1E7B\u1E1D

.. _option_personality#mozilla:

mozilla
=======

Mozilla has made slight adjustments to the Java .properties spec.  Mozilla will
accept UTF-8 encoded strings in the property file and thus does not need
escaped Unicode.  Thus the above string -- ṽḁḽṻḝ -- will not be escaped.
Mozilla property files are thus more useful for non-Latin languages in that
they are actually readable.

Of course this style of file is only used by Mozilla and should not be used for
other projects that follow the Java spec more strictly.

.. _option_personality#skype:

skype
=====

Skype .lang files are .properties files in UTF-16. The & is used as an
accelerator (marked in the PO header).

.. _option_personality#flex:

flex
====

Flex follows the Mozilla approach, a UTF-8 encoded file with no escaped
unicode. We include it as its own dialect for ease of use.

.. _option_personality#strings:

strings
=======

Much Mac OS X and iPhone software is translated using .strings files.  These
are quite different from properties files and we treat them here as key value
files.

The files are in UTF-16 with a few minor escaping conventions.
