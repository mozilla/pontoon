
.. _html:

HTML
****

The Translate Toolkit is able to process HTML files using the :doc:`html2po
</commands/html2po>` converter.

The HTML support is basic, so please be aware of that.

.. _html#conformance:

Conformance
===========

* Can identify almost all tags and attributes that are localisable.
* Does not convert HTML entities (e.g. ``&copy;``) to normal strings
* It does not handle inline elements well and will drop them, so complicated
  HTML might not make it through the filter

.. _html#references:

References
==========

* Using character entities:
  http://www.w3.org/International/questions/qa-escapes
