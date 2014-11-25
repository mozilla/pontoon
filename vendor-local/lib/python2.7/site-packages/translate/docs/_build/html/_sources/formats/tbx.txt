
.. _tbx:

TBX
***
TBX is the `LISA OSCAR standard
<http://www.gala-global.org/lisa-oscar-standards>`_ for terminology and term
exchange.

For information on more file formats, see :doc:`conformance`.


.. _tbx#references:

References
==========

* `Standard home page <http://www.gala-global.org/lisa-oscar-standards>`_
* `Specification
  <http://www.gala-global.org/oscarStandards/tbx/tbx_oscar.pdf>`_
* `ISO 30042
  <http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=45797>`_
  -- TBX is an approved ISO standard
* `Additional TBX resources <http://www.tbxconvert.gevterm.net/>`_

You might also be interested in reading about `TBX-Basic
<http://www.gala-global.org/oscarStandards/tbx/tbx-basic.html>`_ -- a simpler,
reduced version of TBX with most of the useful features included.

Additionally notes and examples about TBX are available in `Terminator TBX
conformance notes
<http://terminator.readthedocs.org/en/latest/tbx_conformance.html>`_ which might
help understanding this format.

Also you might want to use `TBXChecker
<http://sourceforge.net/projects/tbxutil/>`_ in order to check that TBX files
are valid. Check the `TBXChecker explanation
<http://www.tbxconvert.gevterm.net/tbx_checker_explanation.html>`_.


.. _tbx#conformance:

Conformance
===========

Translate Toolkit TBX format support allows:

* Basic TBX file creation
* Creating a bilingual TBX from CSV using :doc:`/commands/csv2tbx`
* Using ``<tig>`` tags only


.. _tbx#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* ``id`` attribute for ``<termEntry>`` tags
* Definitions
* Multiple languages
* Parts of speech
* Multiple translations in the same language
* Cross references
* Context
* Abbreviations
* Synonyms
* ``<ntig>`` tag, read and write

Other features can be picked from the `Terminator TBX conformance notes
<http://terminator.readthedocs.org/en/latest/tbx_conformance.html>`_ which also
include examples and notes about the TBX format.

