
.. _base_classes:

Base classes
************
NOTE: This page is mostly useful for :doc:`developers
</developers/developers>` as it describes some programming detail of the
:doc:`toolkit <index>`.

For the implementation of the different storage classes that the toolkit
supports, we want to define a set of base classes to form a common API for all
formats. This will simplify implementation of new storage formats, and enable
easy integration into external tools, such as Pootle. It will also mean less
duplication of code in similar storage formats.

These ideas explained here should be seen as drafts only.

.. _base_classes#requirements:

Requirements
============
The base classes should be rich enough in functionality to enable users of the
base classes to have access to all or most of the features that are available
in the formats. In particular, the following are considered requirements:

* Seamless and hidden handling of escaping, quoting and character sets
* Parsing a file when given a file name or file contents (whole file in a
  string)
* Writing a file to disk
* Getting and setting source and target languages
* Accessing units, and determining if they are translatable, translated, a
  unique identifier for the unit in the file, etc.
* Support for plural units that can vary between different languages (as the PO
  format allows with msgid_plural, etc.)

Other possibilities:

* Support for variable number of languages in the format. Examples: .txt and
  .properties support one language, PO supports two, :doc:`tmx` supports many.
* Support for "multifiles", in other words a file that contain other entities
  that corresponds to files in other formats. Examples: ZIP and
  :doc:`xliff`. In reality this is only used by some of the converters. This
  isn't present in the base class yet.

All these do not mean that all formats must support al these features, but in
the formats that do support these features, it must be accessible through the
base class, and it must be possible to interrogate the storage format through
the base class to know which features it supports.

.. _base_classes#the_classes:

The classes
===========
A file contains a number of translation units, and possibly a header. Each
translation unit contains one or more strings corresponding to each of the
languages represented in that unit.

.. _base_classes#message/string_multistring:

Message/string (multistring)
----------------------------
This class represents a single conceptual string in a single language. It must
know its own requirements for escaping and implement it internally. Escaped
versions are only used for internal representation and only exposed for file
creation and testing (unit tests, for example).

Note that when storing different plural forms of the same string, they should
be stored in this class. The main object is the singular string, and all of the
string forms can be accessed in a list at x.strings. Most of the time the
object can be dealt with as a single string, only when it is necessary to deal
with plural forms do the extra strings have to be taken into account.

Any string from a plural unit must be a multistring.

.. _base_classes#translation_unit:

Translation unit
----------------
This class represents a unit of one or several related messages/strings. In
most formats the contained strings will be translations of some original
message/string. It must associate a language value with each message/string. It
must know how to join all contained messages/strings to compile a valid
representation. For formats that support at least two languages, the first two
languages will serve as "source" and "target" languages for the common case of
translating from one language into another language.

Some future ideas:

As the number of of languages can be seen as one "dimension" of the translation
unit, plurality can be seen as a second dimension. A format can thus be
classified according to the dimensionality that it supports, as follows:

* .properties files supports one language and no concept of plurals. This
  include most document types, such as .txt, HTML and OpenDocument formats.
* Old style PO files supported two languages and no plurals.
* New style PO files support two languages and any number of plurals as
  required by the target language. The plural forms are stored in the original
  or target strings, as extra forms of the string (See message/string class
  above).
* TMX files support any number of languages, but has no concept of plurality.

Comments/notes are supported in this class. Quality or status information
(fuzzy, last-changed-by) should be stored. TODO: see if this should be on unit
level or language level.

.. _base_classes#store:

Store
-----
This class represents a whole collection of translation units, usually stored
in a single file. It supports the concept of a header, and possibly comments at
file level. A file will not necessarily be contained alone in single file on
disc. See "multifile" below.

.. _base_classes#multifile:

Multifile
---------
This abstraction is only used by a few converters.

This class represents a storage format that contains other files or file like
objects. Examples include ZIP, XLIFF, and OpenOffice SDF files. It must
give access to the contained files, and possibly give access to the translation
units contained in those files, as if they are contained natively.

.. _base_classes#additional_notes:

Additional Notes
****************

Dwayne and I (Andreas) discussed cleaning up the storage base class.  A lot of
what we discussed is related to the above.  A quick summary:

* Implement a new base class.

  * Flesh out the API, clean and clear definitions.
  * Document the API.

* We need to discuss the class hierarchy, e.g.::

    base
         -- po
         -- text
         -- xml
                -- xhtml
                -- lisa
                        -- xliff
                        -- tmx
                        -- tbx

* Clean up converters.

  * Parsing of file content needs to happen only in the storage implementation
    of each filetype/storage type. Currently parsing happens all over the
    place.
  * Currently there are separate conversion programs for each type and
    direction to convert to, e.g. po2xliff and xliff2po (24 commands with lots
    of duplicate code in them). Ideally conversion should be as simple as::

      >>> po_store = POStore(filecontent)
      >>> print str(po_store)
      msgid "bleep"
      msgstr "blorp"
       
      >>> xliff_store = XliffStore(po_store)
      >>> print str(xliff_store)
      <xliff>
        <file>
          <trans-unit>
            <source>bleep</source>
            <target>blorp</target>
          </trans-unit>
        </file>
      </xliff>

Note that the xliffstore is being instantiated using the postore object.  This
works because all the data in any translation store object is accessible via
the same well-defined base API.  A concept class implementing the above code
snippet has already been written.

* Move certain options into their respective storage classes.

  * e.g. the :opt:`--duplicates` option can move into po.py

* Store the meta data for a storage object.

  * Can be implemented as separate sqlite file that accompanies the real file.
  * Features not directly supported by a file format can be stored in the
    metadata file.

* A storage object should know all information pertaining to itself.

  * e.g. "am I monolingual?"

* We should discuss how to make an object aware that it is monolingual,
  bilingual or multilingual.

  * Maybe through mixin-classes?
  * How will the behaviour of a monolingual store differ from a bilingual
    store?
