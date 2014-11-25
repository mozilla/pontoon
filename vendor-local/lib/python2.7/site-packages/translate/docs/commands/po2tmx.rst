
.. _po2tmx:

po2tmx
******

Convert :doc:`Gettext PO </formats/po>` files to a :doc:`/formats/tmx`
translation memory file.  TMX is the Translation Memory eXchange format
developed by OSCAR.

.. [*] OSCAR (Open Standards for Container/Content Allowing Re-use), a special
   interest group of the now defunct LISA (Localization Industry Standards
   Association). The Gala `LISA OSCAR Standards
   <http://www.gala-global.org/lisa-oscar-standards>`_ page has more details on
   the possble future for the standards.

If you are interested in po2tmx, you might also be interested in
:doc:`posegment` that can be used to perform some automated segmentation on
sentence level.

.. _po2tmx#usage:

Usage
=====

::

  po2tmx [options] --language <target> <po> <tmx>

Where:

+-------+----------------+
| <po>  | is a PO file   |
+-------+----------------+
| <tmx> | is a TMX file  |
+-------+----------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in tmx format
-lLANG, --language=LANG  set target language code (e.g. af-ZA) [required]
--source-language=LANG   set source language code (default: en)

.. _po2tmx#examples:

Examples
========

::

  po2tmx -l xh browser.po browser.tmx

Use the Xhosa (*xh*) translations in the PO file *browser.po* to create a TMX
file called *browser.tmx*

.. _po2tmx#bugs_and_issues:

Bugs and issues
===============

.. _po2tmx#markup_stripping:

Markup stripping
----------------

po2tmx conforms to TMX v1.4 without stripping markup.  See the
:doc:`/formats/tmx` conformance page for more details.

It has not been widely tested so your mileage may vary.

.. _po2tmx#tmx_and_po_in_omegat:

TMX and PO in OmegaT
--------------------

In some tools, like OmegaT, PO files are parsed without expanding escaped
sequences, even though such tools use TMX for translation memory.  Keep this in
mind when using po2tmx, because po2tmx converts ``\n`` and ``\t`` to newlines
and tabs in the TMX file.  If such a TMX file is used while translating PO
files in OmegaT, matching will be less than 100%.

In other tools, such as Swordfish, the PO comment "no-wrap" is interpreted in
the same way as the equivalent function in XML, which may also lead to
mismatches if TMXes from po2tmx are used.

There is nothing wrong with po2tmx, but if used in conjunction with tools that
handle PO files differently, it may lead to less than perfect matching.

.. _po2tmx#tips:

Tips
====

.. _po2tmx#tmx_with_only_unique_segments:

TMX with only unique segments
-----------------------------

To create a TMX with no duplicates (in other words, only unique strings), use
msgcat to first create a large PO file with non-uniques removed.
