playdoh
=======

Mozilla's Playdoh is a web application template based on [Django][django].

Patches are welcome! Feel free to fork and contribute to this project on
[github][gh-playdoh].

[django]: http://www.djangoproject.com/
[gh-playdoh]: https://github.com/mozilla/playdoh

Requirements
------------
You need Python 2.6.

This project is set up to use a vendor library, i.e. a subdirectory ``vendor``
that contains all pure Python libraries required by this project.

In addition, there are compiled libraries (such as Jinja2) that you will need
to build yourself, either by installing them from ``pypi`` or by using your
favorite package manager for your OS.

For development, you can run this in a [virtualenv environment][virtualenv]:

    easy_install pip
    pip install -r requirements/compiled.txt

For more information on vendor libraries, read [Packaging in Zamboni][packaging].

[packaging]: http://jbalogh.github.com/zamboni/topics/packages/
[virtualenv]: http://pypi.python.org/pypi/virtualenv

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

