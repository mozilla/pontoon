
.. _levenshtein_distance:

Levenshtein distance
********************
The :wp:`levenshtein distance <Levenshtein_distance>` is used for measuring the
*"distance"* or similarity of two character strings. Other similarity algorithms
can be supplied to the code that does the matching.

This code is used in :doc:`pot2po`, :doc:`tmserver` and `Virtaal
<http://virtaal.org>`_. It is implemented in the toolkit, but can optionally use
the fast C implementation provided by `python-Levenshtein
<https://pypi.python.org/pypi/python-Levenshtein>`_ if it is installed. It is
strongly recommended to have **python-levenshtein** installed.

To exercise the code the classfile *"Levenshtein.py"* can be executed directly
with:

.. code-block:: bash

    $ python Levenshtein.py "The first string." "The second string"


.. note:: Remember to quote the two parameters.


The following things should be noted:

* Only the first ``MAX_LEN`` characters are considered. Long strings differing
  at the end will therefore seem to match better than they should. A penalty is
  awarded if strings are shortened.
* The calculation can stop prematurely as soon as it realise that the supplied
  minimum required similarity can not be reached. Strings with widely different
  lengths give the opportunity for this shortcut. This is by definition of the
  Levenshtein distance: the distance will be at least as much as the difference
  in string length. Similarities lower than your supplied minimum (or the
  default) should therefore not be considered authoritative.


.. _levenshtein_distance#shortcommings:

Shortcommings
=============

The following shortcommings have been identified:

* **Cases sensitivity:** *'E'* and *'e'* are considered different characters and
  according differ as much as *'z'* and *'e'*. This is not ideal, as case
  differences should be considered less of a difference.
* **Diacritics:** *'ê'* and *'e'* are considered different characters and
  according differ as much as *'z'* and *'e'*. This is not ideal, as missing
  diacritics could be due to small input errors, or even input data that simply
  do not have the correct diacritics.
* **Similar but different words:** Words that have similar characters, but are
  different, could increase the similarity beyond what is wanted. The sentences
  *"It is though."* and *"It is dough."* differ markedly semantically, but score
  similarity of almost 85%. A possible solution is to do an additional
  calculation based on words, instead of characters.
* **Whitespace:** Differences in tabs, newlines, and space usage should perhaps
  be considered as a special case.
