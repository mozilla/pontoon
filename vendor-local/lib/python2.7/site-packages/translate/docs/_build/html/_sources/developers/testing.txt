.. _testing:

Testing
=======

Our aim is that all new functionality is adequately tested. Adding tests for
existing functionality is highly recommended before any major reimplementation
(refactoring, etcetera).

We use `py.test`_ for (unit) testing. You need at least pytest >= 2.2.

To run tests in the current directory and its subdirectories:

.. code-block:: bash

    $ py.test  # runs all tests
    $ py.test storage/test_dtd.py  # runs just a single test module

We use several py.test features to simplify testing, and to suppress errors in
circumstances where the tests cannot possibly succeed (limitations of
tests and missing dependencies).


Skipping tests
--------------

Pytest allows tests, test classes, and modules to be skipped or marked as
"expected to fail" (xfail).
Generally you should *skip* only if the test cannot run at all (throws uncaught
exception); otherwise *xfail* is preferred as it provides more test coverage.

importorskip
^^^^^^^^^^^^

.. the ~ in this :func: reference suppresses all but the last component

Use the builtin :func:`~pytest:_pytest.runner.importorskip` function
to skip a test module if a dependency cannot be imported:

.. code-block:: python

    from pytest import importorskip
    importorskip("vobject")

If *vobject* can be imported, it will be; otherwise it raises an exception
that causes pytest to skip the entire module rather than failing.

skipif
^^^^^^

Use the ``skipif`` decorator to :ref:`mark tests to be skipped <pytest:skipif>`
unless certain criteria are met.  The following skips a test if the version of
*mymodule* is too old:

.. code-block:: python

    import mymodule

    @pytest.mark.skipif("mymodule.__version__ < '1.2'")
    def test_function():
        ...

In Python 2.6 and later, you can apply this decorator to classes as well as
functions and methods.

It is also possible to skip an entire test module by creating a ``pytestmark``
static variable in the module:

.. code-block:: python

    # mark entire module as skipped for py.test if no indexer available
    pytestmark = pytest.mark.skipif("noindexer")

xfail
^^^^^

Use the ``xfail`` decorator to :ref:`mark tests as expected to fail
<pytest:xfail>`. This allows you to do the following:

* Build tests for functionality that we haven't implemented yet
* Mark tests that will fail on certain platforms or Python versions
* Mark tests that we should fix but haven't got round to fixing yet

The simplest form is the following:

.. code-block:: python

    from pytest import pytest.mark
    
    @mark.xfail
    def test_function():
        ...

You can also pass parameters to the decorator to mark expected failure only
under some condition (like *skipif*), to document the reason failure is
expected, or to actually skip the test:

.. code-block:: python

    @mark.xfail("sys.version_info >= (3,0)")  # only expect failure for Python 3
    @mark.xfail(..., reason="Not implemented")  # provide a reason for the xfail
    @mark.xfail(..., run=False)  # skip the test but still regard it as xfailed


Testing for Warnings
--------------------

deprecated_call
^^^^^^^^^^^^^^^

The builtin :func:`~pytest:pytest.deprecated_call` function checks that a
function that we run raises a DeprecationWarning:

.. code-block:: python

    from pytest import deprecated_call
 
    def test_something():
        deprecated_call(function_to_run, arguments_for_function)

recwarn
^^^^^^^

The |recwarn plugin|_ allows us to test for other warnings. Note that
``recwarn`` is a funcargs plugin, which means that you need it in your test
function parameters:

.. code-block:: python

    def test_example(recwarn):
        # do something
        w = recwarn.pop()
        # w.{message,category,filename,lineno}
        assert 'something' in str(w.message)


.. _py.test: http://pytest.org/

.. _recwarn plugin: http://pytest.org/latest/recwarn.html
.. |recwarn plugin| replace:: *recwarn plugin*
.. we use |recwarn plugin| here and in ref above for italics like :ref:


Command Line Functional Testing
================================

Functional tests allow us to validate the operation of the tools on the command
line.  The execution by a user is simulated using reference data files and the
results are captured for comparison.

The tests are simple to craft and use some naming magic to make it easy to
refer to test files, stdout and stderr.

File name magic
---------------

We use a special naming convention to make writing tests quick and easy.  Thus
in the case of testing the following command:

.. code-block:: bash

   $ moz2po -t template.dtd translations.po translated.dtd

Our test would be written like this:

.. code-block:: bash

   $ moz2po -t $one $two $out

Where ``$one`` and ``$two`` are the input files and ``$out`` is the result file
that the test framework will validate.

The files would be called:

===========================    ============   =========   ===================
File                            Function       Variable    File naming conventions
===========================    ============   =========   ===================
test_moz2po_help.sh             Test script    -           test_${command}_${description}.sh
test_moz2po_help/one.dtd        Input          $one        ${testname}/${variable}.${extension}
test_moz2po_help/two.po         Input          $two        ${testname}/${variable}.${extension}
test_moz2po_help/out.dtd        Output         $out        ${testname}/${variable}.${extension}
test_moz2po_help/stdout.txt     Output         $stdout     ${testname}/${variable}.${extension}
test_moz2po_help/stderr.txt     Output         $stderr     ${testname}/${variable}.${extension}
===========================    ============   =========   ===================

.. note:: A test filename must start with ``test_`` and end in ``.sh``.  The
   rest of the name may only use ASCII alphanumeric characters and underscore
   ``_``.

The test file is placed in the ``tests/`` directory while data files are placed
in the ``tests/data/${testname}`` directory.

There are three standard output files:

1. ``$out`` - the output from the command
2. ``$stdout`` - any output given to the user
3. ``$stderr`` - any error output

The output files are available for checking at the end of the test execution
and a test will fail if there are differences between the reference output and
that achieved in the test run.

You do not need to define reference output for all three, if one is missing
then checks will be against ``/dev/null``.

There can be any number of input files.  They need to be named using only ASCII
characters without any punctuation.  While you can give them any name we
recommend using numbered positions such as one, two, three.  These are
converted into variables in the test framework so ensure that none of your
choices clash with existing bash commands and variables.

Your test script can access variables for all of your files so e.g.
``moz2po_conversion/one.dtd`` will be referenced as ``$one`` and output
``moz2po_conversion/out.dtd`` as ``$out``.


Writing
-------

The tests are normal bash scripts so they can be executed on their own.  A
template for a test is as follows:

.. literalinclude:: ../../tests/cli/example_test.sh
   :language: bash

For simple tests, where we diff output and do the correct checking of output
files, simply use ``check_results``.  More complex tests need to wrap tests in
``start_checks`` and ``end_checks``.

.. code-block:: bash

   start_checks
   has $out
   containsi_stdout "Parsed:"
   end_checks

You can make use of the following commands in the ``start_checks`` scenario:

=========================== ===========================================
Command                      Description
=========================== ===========================================
has $file                    $file was output and it not empty
has_stdout                   stdout is not empty
has_stderr                   stderr is not empty
startswith $file "String"    $file starts with "String"
startswithi $file "String"   $file starts with "String" ignoring case
startswith_stdout "String"   stdout starts with "String"
startswithi_stdout "String"  stdout starts with "String" ignoring case
startswith_stderr "String"   stderr starts with "String"
startswithi_stderr "String"  stderr starts with "String" ignoring case
contains $file "String"      $file contains "String"
containsi $file "String"     $file contains "String" ignoring case
contains_stdout "String"     stdout contains "String"
containsi_stdout "String"    stdout contains "String" ignoring case
contains_stderr "String"     stderr contains "String"
containsi_stderr "String"    stderr contains "String" ignoring case
endswith $file "String"      $file ends with "String"
endswithi $file "String"     $file ends with "String" ignoring case
endswith_stdout "String"     stdout ends with "String"
endswithi_stdout "String"    stdout ends with "String" ignoring case
endswith_stderr "String"     stderr ends with "String"
endswithi_stderr "String"    stderr ends with "String" ignoring case
=========================== ===========================================


--prep
^^^^^^

If you use the --prep options on any test then the test will change behavior.
It won't validate the results against your reference data but will instead
create your reference data.  This makes it easy to generate your expected
result files when you are setting up your test.
