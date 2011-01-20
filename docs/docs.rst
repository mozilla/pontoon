.. _docs:

=========================
Documentation with Sphinx
=========================

*(Borrowed from Zamboni)*

For a reStructuredText Primer, see http://sphinx.pocoo.org/rest.html.


Sections
--------

Sphinx doesn't care what punctuation you use for marking headings, but each new
kind that it sees means one level lower in the outline.  So, ::

    =========
    Heading 1
    =========

    Heading 2
    ---------

will correspond to ::

    <h1>Heading 1</h1>
    <h2>Heading 2</h2>

For consistency, this is what I'm using for headings in Zamboni::

    =========
    Heading 1
    =========

    Heading 2
    ---------

    Heading 3
    ~~~~~~~~~

    Heading 4
    *********

    Heading 5
    +++++++++

    Heading 6
    ^^^^^^^^^

Use two newlines prior to a new heading.  I'm only using one here for space
efficiency.


Sphinx Extras
-------------

Use ``:src:`path/to/file.py``` to link to source files online.  Example:
:src:`settings.py`.


Vim
---

Here's a nice macro for creating headings::

    let @h = "yypVr"


Compiling Documentation
-----------------------

Playdoh hosts its documentation on `github pages
<http://mozilla.github.com/playdoh/>`_. When you change the docs, make sure
they still build properly and look all right locally::

    cd docs && make html && open _build/html/index.html

If they do, run a build and push it to gh-pages::

    ./build-github.zsh
