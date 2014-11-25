
.. _csv:

CSV
***
CSV (Comma Separated Values) is a simple file format for general data
interchange. It can be used in the toolkit for simple data interchange, and can
be edited with most spreadsheet programs. There is no formal specification for
the CSV file format, but more information can be acquired from
:wp:`Comma-Separated Values <Comma-separated_values>`

.. _csv#conformance:

Conformance
===========
CSV files were initially used to convert from and to :doc:`po files <po>`, and
therefore contained three columns as follows:

+------------+---------------------------------------------------------------+
| Column     | Description                                                   |
+============+===============================================================+
| location   | A column with the location of the original msgid (in other    |
|            | words, a line in a programming source file, as indicated in   |
|            | the #: comments of PO files).                                 |
+------------+---------------------------------------------------------------+
| source     | The source text (or msgid)                                    |
+------------+---------------------------------------------------------------+
| target     | The target text (or msgstr)                                   |
+------------+---------------------------------------------------------------+

Tabs and newlines are maintained, although it is not clear how easy it is to
edit these things in a spreadsheet.

Quoting is a problem, because the different spreadsheet programs handle these
things differently. Notably, Microsoft's excel handles single quotes slightly
differently. In future, it might be worthwhile to handle excel CSV as a
different format from other CSV files. An entry like 'mono' is ambiguous as it
is not sure whether this refers simply to the word *mono* or to the entry
*'mono'* quoted with single quotes. (Example from Audacity pot file)

