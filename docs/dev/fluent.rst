Integration with fluent
=======================

Pontoon is able to synchronize translations produced by libraries provided by Project Fluent and provides
advanced editor for translators.

Because of our very close integration, we'll need to compile the fresh versions of javascript/python libraries
in order to provide new features.

It's important to remember to update both packages:
* python-fluent (responsible for e.g. server-side sync process)
* fluent-syntax (required by the fluent editor)

How to build the fresh version of fluent-syntax.js
--------------------------------------------------

.. code-block:: bash
    git clone https://github.com/projectfluent/fluent.js
    cd fluent.js
    npm install
    cd fluent-syntax
    make build
    cp fluent-syntax.js <your pontoon directory>/pontoon/base/static/js/lib/fluent-syntax.js