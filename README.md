Pontoon
=======
This is a proof-of-concept implementation of an in-place website localization tool, as [outlined by Austin King][outline]. Please note that Pontoon is in a very early alpha version, under heavy development, and unlikely to do much out of the box. If you are interested in the technology, feel free to step by `#pontoon` on <irc://irc.mozilla.org> or get more information from a [wiki][wiki].

Client components
-----------------

The client components run on the user's computer and allow them to localize a document by presenting both a list of extracted entities from the document and specific widgets that overlay the document and enable in-page translation. Different clients can be written, e.g. web client, jetpack client, bookmarklet etc.

Hook components
---------------

The hook component(s) are the part of the web app that hook into the target project and prepare it to work with the client. As of yet, these components are only available in PHP.

Server component
----------------

The server component is a django based webapp that provides an API necessary for the client. It provides user authentication, accepts partial and full translations of the document, presents information on the current status of the document's translation, and synchronizes work between multiple localizers.

Dependencies
------------
* Apache
* PHP
* Django 

Usage
-----
Web client:

* Map /pontoon on a web server to the root of this project.
* Point your browser to /pontoon.
* Click on the Demo link.

Django server ([Django][django] is required):

* `cd server`
* `python manage.py runserver 0.0.0.0:8000`

To use Microsoft Translator API for machine translation, obtain a valid API key from the [Bing Developer Center][bdc] and store it in a variable Pontoon._app._mt in your local JS settings file client/lib/js/local-settings.js.

Store Pontoon client path in the $path variable in your local PHP settings file hook/php/local-settings.php.

Contributors
------------
* Matjaž Horvat <matjaz@mozilla.com>
* Frederic Wenzel <fwenzel@mozilla.com>
* Zbigniew Braniecki <gandalf@mozilla.com>
* Austin King <aking@mozilla.com>

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/
[outline]:  http://ozten.com/psto/2009/08/14/a-sketch-of-po-liveedit/   "A Sketch of PO LiveEdit"
[wiki]:  https://wiki.mozilla.org/L10n:Pontoon   "L10n:Pontoon - MozillaWiki"
[bdc]: http://www.bing.com/developers/createapp.aspx   "Bing Developer Center"
[django]: https://www.djangoproject.com/   "Django"
