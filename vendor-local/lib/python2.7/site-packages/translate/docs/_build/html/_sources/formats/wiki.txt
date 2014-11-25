
.. _wiki:

Wiki Syntax
***********

The Translate Toolkit can manage Wiki syntax pages.  This is implemented as
part of the :doc:`text <text>` format and the conversion is supported in
:doc:`txt2po </commands/txt2po>`.

Those who edit wikis will appreciate that wiki text is simply a normal text
document edited using a form of wiki syntax.  Whether the final storage is a
database or a flat file the part that a user edits is a simple text file.

The format does not support all features of the wiki syntax and will simply
dump the full form if it doesn't understand the text.  But structures such as
headers and lists are understood and the filter can remove these are correctly
add them.

.. _wiki#supported_wiki_formats:

Supported Wiki Formats
======================

The following is a list of the wikis supported together with a list of the
items that we can process:

* `dokuwiki <http://wiki.splitbrain.org/wiki:dokuwiki>`_ -- heading, bullet,
  numbered list
* `MediaWiki <http://www.mediawiki.org/wiki/MediaWiki>`_ -- heading, bullet,
  numbered list

.. _wiki#possible_uses:

Possible uses
=============

As part of a localisation process for a wiki this format and the filters could
be used to provide a good localisation of existing wiki content.

With further enhancement the tool could probably be capable of converting from
one wiki syntax to another, but that is of course not its main aim

.. _wiki#additional_notes_on_mediawiki:

Additional notes on MediaWiki
=============================

Media wiki can also export in XML format, see
http://en.wikipedia.org/wiki/Special:Export and
http://www.mediawiki.org/wiki/Manual:Parameters_to_Special:Export this however
exports in XML so not directly usable by txt2po.

For importing please see http://en.wikipedia.org/wiki/Help:Import this is
disabled on most wikis so not directly usable currently.

