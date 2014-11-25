
.. _posegment:

posegment
*********

posegment takes a Gettext PO or XLIFF file and segments the entries, generating
a new file with revised and smaller translation units.

This is useful for the creation of a file that can be used as a Translation
Memory as you should get better matching after you have exposed translated
sentences that might occur elsewhere in your work.

Posegment won't do very advanced sentence boundary detection and alignment, but
has customisations for the punctuation rules of several languages (Amharic,
Afrikaans, Arabic, Armenian, Chinese, Greek, Japanese, Khmer, Oriya, Persian).
For the purpose of increasing your TM (as described below), it is already very
useful. Give it a try and help us to improve it even more for your language.

.. _posegment#usage:

Usage
=====

::

  posegment [options] <input> <segmented>

Where:

+--------------+-------------------------------------------------+
| <input>      | translations to be segmented                    |
+--------------+-------------------------------------------------+
| <segmented>  |  translations segmented at the sentence level   |
+--------------+-------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose
                       <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in pot format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-P, --pot             output PO Templates (.pot) rather than PO files (.po)
-l LANG, --language=LANG
                      the target language code
--source-language=LANG
                      the source language code (default 'en')
--keepspaces          Disable automatic stripping of whitespace
--only-aligned        Removes units where sentence number does not
                      correspond

.. _posegment#examples:

Examples
========

You want to reuse all of your Pidgin translations in another Instant
Messenger::

  posegment pidgin-af.po pidgin-af-segmented.po

Now all of our Pidgin translation are available, segmented at a sentence level,
to be used as a Translation Memory for our other translation work.

You can do the same at a project level.  Here we want to segment all of our
OpenOffice.org translation work, a few hundred files::

  posegment af/ af-segmented/

We start with all our files in ``af`` which are now duplicated in
``af-segmented`` except files are now fully segmented.

.. _posegment#issues:

Issues
======

* If the toolkit doesn't have segmentation rules for your language then it will
  default to English which might be incorrect.
* Segmentation does not guarantee reuse as your TM software needs to know how
  to segment when matching. If you use software that doesn't do segmentation,
  you can consider joining the original and the segmented files together with
  msgcat, to get the best of both worlds.
* You cannot (yet) use the tool to break a file into segments, translate, and
  then recreate as the segmented file does not know which parts should be
  joined together to recreate a file.
