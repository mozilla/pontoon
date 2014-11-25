
.. _translate_toolkit_developers_guide:

Translate Toolkit Developers Guide
**********************************

The goal of the translate toolkit is to simplify and unify the process of
translation.

.. _developers#history:

History
=======

The initial toolkit was designed to convert Mozilla .dtd and .properties files
into Gettext PO format.  The logic was not that PO was in any way superior but
that by simplifying the translations process i.e. allowing a translator to use
one format and one tool that we could get more people involved and more
translators.

The tools have now evolved to include other formats such as OpenOffice.org and
the goal is still to migrate various formats to a common format, PO and in the
future XLIFF as more tools become available for that format.

These tools we group as converters.  Along the way we developed other tools
that allowed us to manipulate PO files and check them for consistency.  As we
evolved the converter tools we have also improved and abstracted the classes
that read the various file types.  In the future we hope to define these better
so that we have a more or less stable API for converters.

.. _developers#resources:

Resources
=========

.. _developers#git_access:

Git access
----------
Translate Toolkit uses Git as a Version Control System. You can directly clone
the translate repository or fork it at GitHub.

::

  git clone https://github.com/translate/translate.git

.. _developers#bugzilla:

Issues
------

* https://github.com/translate/translate/issues

.. _developers#communication:

Communication
-------------

* IRC channels:

  * `Development <irc://irc.freenode.net/#pootle-dev>`_ - no support related questions.
  * `Help <irc://irc.freenode.net/#pootle>`_

* `Developers mailing list <https://lists.sourceforge.net/lists/listinfo/translate-devel>`_
* `Commits to version control <https://lists.sourceforge.net/lists/listinfo/translate-cvs>`_

.. _developers#working_with_bugzilla:

Working with Bugzilla
=====================
When you close bugs ensure that you give a description and git hash for the
fix.  This ensures that the reporter or code reviewer can see your work and has
an easy method of finding your fix.  This is made easier by GitHub's Bugzilla
integration.

Automated Bugzilla update from commits
--------------------------------------

Github will post comments on Bugzilla bugs when the commit messages make
references to the bug by its bug number.

- Bugs are recognised by the following format (which are case-insensitive)::

    Bug 123

- Multiple bugs can be specified by separating them with a comma, ampersand,
  plus or "and"::

    Bug 123, 124 and 125

- Commits to all branches will be processed.
- If there is a "fix", "close", or "address" before the bug then that bug is
  closed. ::

    Fix bug 123

.. _developers#source_code_map:

Source code map
===============

The source code for the tools is hosted on `GitHub
<https://github.com/translate/translate>`_.  This rough map will allow you to
navigate the source code tree:

* convert -- convert between different formats and PO format
* filters -- :doc:`/commands/pofilter` and its helper functions (badly named,
  it is really a checking tool)
* storage -- all base file formats: XLIFF, .properties, OpenOffice.org, TMX,
  etc.
* misc -- various helper functions
* tools -- all PO manipulation programs: :doc:`/commands/pocount`,
  :doc:`/commands/pogrep`, etc
* lang -- modules with data / tweaks for various languages
* search -- translation memory, terminology matching, and indexing / searching
* share -- data files

.. _developers#setup:

Setup
=====

The toolkit is installed by running::

  ./setup.py install

As root

The various setup options are yours to explore

.. _developers#general_overview_of_the_programs:

General overview of the programs
================================

Each tool in the toolkit has both a core program and a command line wrapper.
For example the oo2po converter:

* oo2po -- the command line tool
* oo2po.py -- the core program

This is done so that the tools can be used from within the Pootle server thus
reusing the toolkit easily.

.. _developers#command_line_options:

Command line options
--------------------

Getting lost with the command line options?  Well you might want to volunteer
to move some of them into configuration files.  But in terms of programming you
might be confused as to where they are located.  Many of the command line
options are implemented in each tool.  Things such as :opt:`--progress` and
:opt:`--errorlevel` are used in each program.  Thus these are abstracted in
**misc/optrecurse.py**.  While each tools unique command line options are
implemented in **xxx.py**.

.. _developers#converters:

Converters
==========

The converters each have a class that handles the conversion from one format to
another.  This class has one important method **convertfile** which handles the
actual conversion.

A function **convertXXX** manages the conversion for the command line
equivalent and essentially has at least 3 parameters: inputfile, outputfile and
templatefile.  It itself will call the conversion class to handle conversion of
individual files.  Recursing through multiple files is handled by the
optrecurse.py logic.

The converters **main** function handles any unique command line options.

Where we are headed is to get to a level where the storage formats themselves
are more aware of themselves and their abilities.  Thus the converter could end
up as one program that accepts storage format plugins to convert from anything
to almost anything else.  Although our target localisation formats are PO and
XLIFF only.

If you want to create a new converter it is best to look at a simple instance
such as :doc:`/commands/csv2tbx` or :doc:`/commands/txt2po` and their
associated storage classes.  The :doc:`storage base class documentation
</api/storage>` will give you the information you need for the storage class
implementation.

.. _developers#tools:

Tools
=====

The tools in some way copy the logic of the converters.  We have a class so
that we can reuse a lot of the functionality in Pootle.  We have a core
function that take: input, output and templates.  And we have a **main**
function to handle the command line version.

:doc:`/commands/pocount` should be converted to this but does not follow this
conventions.  In fact pocount should move the counting to the storage formats
to allow any format to return its own word count.

.. _developers#checks:

Checks
======

There's really only one, :doc:`/commands/pofilter`.  But there are lots of
helper functions for pofilter.  pofilters main task is to check for errors in
PO or XLIFF files.  Here are the helper file and their descriptions.

* autocorrect.py -- when using :opt:`--autocorrect` it will attempt some basic
  corrections found in this file
* checks.py -- the heart. This contains: the actual checks and their error
  reports, and defined variables and accelerators for e.g, :opt:`--mozilla`
* decorations.py -- various helper functions to identify accelerators,
  variables and markers
* helpers.py -- functions used by the tests
* prefilters.py -- functions to e.g. remove variables and accelerators before
  applying tests to the PO message

pofilter is now relatively mature.  The best areas for contributions are:

* more tests
* language specific configuration files
* tests for the tests -- so we don't break our good tests
* defining a config files scheme to do cool stuff off of the command line.
  Globally enable or disable tests based on language, etc
* some approach to retesting that would remove '# (pofilter)' failure markings
  if the test now passes.
* ability to mark false positives

The :doc:`API documentation </api/filters>` is a good start if you want to add
a new tests.  To add a new language have a look at a language you understand
amongst those already implemented.

.. _developers#storage:

Storage
=======

These are the heart of the converters.  Each destination storage format is
implemented in its own file.  Up until toolkit version 0.8, there was no
formally defined API (the tools have been evolving and only recently
stabilised), but they generally followed this structure.  These classes are
defined:

* XXelement -- handles the low level individual elements of the file format.
  e.g. PO message, CSV records, DTD elements
* XXfile -- handles the document or file level of the format.  Eg a PO file, a
  CSV file a DTD file

  * fromlines -- read in a file and initialise the various elements
  * tolines -- convert the elements stored in XXelements and portions in XXfile
    to a raw file in that format

In the XML based formats e.g.  TMX, XLIFF and HTML there is usually just an
extended parser to manage the file creation.

Within each storage format there are many helper functions for escaping and
managing the unique features of the actual format.

You can help by:

* abstracting more of the functions and documenting that so that we can get a
  better API
* adding other formats and converters e.g. .DOC, .ODF and others
* helping us move to a position where any format should convert to the base
  format: PO and in the future XLIFF without having to create a specific
  converter wrapper.
* Ensuring that our formats :doc:`conform to the standards
  </formats/conformance>`

.. _developers#base_classes:

Base Classes
------------

From toolkit 0.9 onwards, we are moving towards basing all storage formats on a
set of :doc:`base classes </formats/base_classes>`, in the move to a universal
API.  We're also fixing things so that escaping is much more sane and handled
within the class itself not by the converters.

In base classes we have different terminology

* XXXunit = XXXelement
* XXXstore = XXXfile

We have also tried to unify terminology but this has been filtered into the old
classes as far as possible.
