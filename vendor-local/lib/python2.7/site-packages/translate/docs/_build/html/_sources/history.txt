
.. _history:

History of the Translate Toolkit
********************************

This is a short history of the Translate Toolkit. In many ways written so that
people who see problems in the toolkit can understand how it evolved and where
it is going.

.. _history#conception:

Conception
==========

The toolkit was developed by David Fraser while working for `Translate.org.za
<http://translate.org.za>`_.  Initially Translate.org.za had focussed on
translating KDE into South Africa languages, this work was PO based.  The next
project was to translate Mozilla which used a combination of DTD and
.properties files.  The Mozilla project used a tool called Mozilla Translator,
which mostly worked although it was not as feature rich as KBabel that was
being used to manage PO translations.  A decision was made to create a set of
tools that could convert the DTD and .properties files into PO files.  The
advantage being that translators would not need to learn new tools, that
existing translations could be leveraged and that the resultant files, being
bilingual, would make it easier to upgrade and manage translations.

Thus was born what initially was called the mozpotools.

.. _history#growth:

Growth
======

The first problem with the tools was that it was possible to break Mozilla
translations.  This was a combination of the fact that translators would often
translate variables such as &browserName; and that the toolkit had developed a
method of folding labels and accelerators into one PO field.  These breakages
where presented as broken XML.  Thus was born pofilter which allowed us to
check the translations for problems in variables and accelerators.  pomerge its
sister allowed us to merge the corrections back into the main.  We also
developed pocount which allowed us to for the first time get a real feel of the
volume of work required in translating a PO file.

.. _history#expansion:

Expansion
=========

Of course once you can convert the convoluted Mozilla translations then you
realise you can do anything.  A key addition was the converter for
OpenOffice.org but also added where TMX, Qt .ts, txt and OpenOffice.org SXW
files.

The key being that files are converted to PO to allow translations and use of
the Gettext tools and existing PO files.

.. _history#pootle:

Pootle
======

Initially started as a separate project to allow online translation it was soon
realised that the toolkit being file based gave all the infrastructure to allow
Pootle to be a wrapper around the toolkit.  So a file based, web translation
tool was created.

.. _history#wordforge_project:

WordForge project
=================

In 2006 with funding from the `Open Society Institute
<http://www.opensocietyfoundations.org/>`_ (OSI) and `IDRC
<http://www.idrc.ca/>`_ the toolkit was adapted to allow many core changes.
The first being to introduce the concept of a base class from which PO and
XLIFF storage formats are derived.  This allowed tools to be adapted to allow
output to XLIFF or PO files.  The tools themselves where adapted to allow them
to work with the core formats XLIFF and PO as well as all base class derived
formats.  Thus we can count XLIFF, PO, MO and other formats.

Additional contributions during this phase where the adaptation of Pootle to
use XLIFF as well as PO.  The creation of tools to manage translation memory
files and glossary files.

The toolkit was also adapted to make dealing with encodings, plural forms, and
escaping easier and more consistent throughout the code.  Many but not all of
the formats where converted to the base class.

As part of the WordForge project Pootling was created which in the same way
that Pootle is a web-based wrapper around the toolkit so Pootling is a GUI
wrapper around the toolkit.

.. _history#anloc_project:

ANLoc project
=============
The `African Network for Localisation <http://africanlocalisation.net>`_
provided the opportunity for further improvements to the project.  We saw the
first official releases of `Virtaal <http://virtaal.org>`_ and massive
improvements to all the translation tools.

Format support improved a lot, with several bilingual file formats now support
(Wordfast TM, Qt TS, etc.), and several monolingual file formats (PHP arrays,
video subtitles, Mac OS X strings, etc.).

.. _history#the_future:

The Future
==========

The toolkit continues to evolve with clean-up focused in various areas:

* Pulling features out of Pootle that should be in the Toolkit
* Cleaning up storage classes and converters to be XLIFF/PO interchangeable
* Cleaning up the converters to use only base class features and migrating code
  from the converters to the storage class
* Adding storage classes as needed
* Optimisation where needed

The toolkit continues to serve as the core for the command line tools and for
Pootle.  Key new features:

* Process Management
