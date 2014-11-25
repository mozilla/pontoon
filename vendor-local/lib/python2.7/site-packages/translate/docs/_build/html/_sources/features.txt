
.. _features:

Features
********

* Work with **ONE localisation format**.  You'll no longer be editing DTD files
  in one tool, .properties in another, OpenOffice GSI in a third.  Simply do
  all your localisation in a PO or XLIFF editor
* **Converters** for a number of :doc:`formats <formats/index>`

  * OpenOffice.org SDF/GSI
  * Mozilla: .properties, DTD, XHTML, .inc, .ini, etc
  * Others: Comma Separated Value, TMX, XLIFF, TBX, PHP, WordFast TXT, Qt .ts,
    txt, .ini, Windows .rc, ical, subtitles, Mac OS X strings

* **File access to localization files** through the format API in all the above
  formats, as well as .qph, .qm, .mo
* Output **valid target file** types.  We make sure that your output files
  (e.g. .properties) contain all comments from the original file and preserves
  the layout of the original as far as possible.  If your PO entry is marked as
  fuzzy we use the English text, not your half complete translation.  The
  converters for OpenOffice.org and Mozilla formats will also perform simple
  checks and corrections to make sure you have none of those hard to find
  localisation bugs.
* Our checker has over :doc:`42 checks </commands/pofilter_tests>` to find
  errors such as: missing or translated variables, missing accelerator keys,
  bad escaping, start capitalisation, missing sentences, bad XML and much more.
* Language awareness, taking language conventions for capitalisation, quotes
  and other punctuation into account
* **Find conflicting translations** easily, cases where you have translated a
  source word differently or used a target word for 2 very different English
  concepts
* **Extract messages** using simple text or a regular expression allowing you
  to quickly find and extract words that you need to fix due to glossary
  changes.
* **Merge snippets** of PO files into your existing translations.
* Create word, string and file **counts** of your files.  Making it much easier
  to budget time as string counts do not give you a good indication of expected
  work.
* Create a set of PO files with **debugging** entries to allow you to easily
  locate the source of translations.  Very useful in OpenOffice.org which
  provides scant clues as to where the running application has sourced the
  message.

The Translate Toolkit is also a **powerful API** for writing translation and
localisation tools, already used by our own and several other projects. See the
:doc:`base class <formats/base_classes>` section for more information.
