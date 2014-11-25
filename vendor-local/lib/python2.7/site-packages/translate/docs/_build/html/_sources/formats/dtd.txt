
.. _dtd:

Mozilla DTD format
******************

Mozilla makes use of a .dtd file to store many of its translatable elements,
the :doc:`moz2po </commands/moz2po>` converter can handle these.

.. _dtd#references:

References
==========

* `XML specification <http://www.w3.org/TR/REC-xml/>`_

.. _dtd#features:

Features
========

* Comments -- these are handled correctly and integrated with the unit
* Accelerators -- if a unit has an associated access key entry then these are
  combined into a single unit
* Translator directive -- all LOCALIZATION NOTE items such as DONT_TRANSLATE
  are handled and such items are discarded
* Entities -- some entities such as ``&amp;`` or ``&quot;`` are expanded when
  reading DTD files and escaped when writing them, so that translator see and
  type ``&`` and ``"`` directly

.. _dtd#issues:

Issues
======

* We don't expand some character entities like ``&lt;``, ``&#38;`` -- this
  doesn't break anything but it would be nicer to see © rather than ``&copy;``
