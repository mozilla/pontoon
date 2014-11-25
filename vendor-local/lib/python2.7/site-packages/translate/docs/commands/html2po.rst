
.. _html2po:
.. _po2html:

html2po
*******

Convert translatable items in HTML to the PO format.

.. _html2po#usage:

Usage
=====

::

  html2po [options] <html> <po>
  po2html [options] <po> <html>

Where:

+---------+-----------------------------------------------+
| <html>  | is an HTML file or a directory of HTML files  |
+---------+-----------------------------------------------+
| <po>    | is a PO file or directory of PO files         |
+---------+-----------------------------------------------+

Options (html2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in htm, html, xhtml formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
-u, --untagged       include untagged sections
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2html):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in htm, html formats
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in htm, html formats
-S, --timestamp      skip conversion if the output file has newer timestamp
-wWRAP, --wrap=WRAP  set number of columns to wrap html at
--notidy             don't use tidy to clean up HTML, even if installed (new in version 1.2.1)
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _html2po#examples:

Examples
========

::

  html2po -P site pot

This will find all HTML files (.htm, .html, .xhtml) in *site* convert them to
POT files and place them in *pot*::

  po2html -t site xh site-xh

All the PO translations in *xh* will be converted to html using html files in
*site* as templates and outputting new translated HTML files in *site-xh*

.. _html2po#bugs:

Bugs
====

We don't hide enough of some of the tags, e.g. <a> tags have too much exposed,
we should expose only what needs to be translated and allow the changing on
position of the tag within the translation block.  Similarly there is some
markup that could be excluded e.g. <b> tags that appear at the start and end of
a msgid, i.e. they don't need placement from the translator.

If the HTML is indented you get very odd msgid's

Some items end up in the msgid's that should not be translated

It might be worth investigating
http://opensource.bureau-cornavin.com/html2pot-po2html/index.html which uses
XSLT to transform XHTML to Gettext PO
