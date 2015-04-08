Pontoon
=======
Pontoon enables localizers to translate web apps and web sites in place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag. [Localizer Docs](https://developer.mozilla.org/en-US/docs/Localizing_with_Pontoon).

To enable localization of your site with Pontoon, include a script to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags. [Developer Docs](https://developer.mozilla.org/en-US/docs/Implementing_Pontoon_Mozilla).

Installation
------------
Pontoon is based on [Playdoh](http://playdoh.readthedocs.org/en/latest/), so it's easy to set it up. Follow the steps below.

1. Clone this repository or your [fork](http://help.github.com/fork-a-repo/):
 * `git clone --recursive https://github.com/mathjazz/pontoon.git`
 * `cd pontoon`
2. Create and set up [virtual environment](http://www.virtualenv.org/en/latest/index.html):
 * `virtualenv --no-site-packages env`
 * `source env/bin/activate`
 * `pip install -r requirements/compiled.txt -r requirements/prod.txt`
3. Configure [settings](#local-settings):
 * `cp settings/local.py-dist settings/local.py`
4. Set up database:
 * `mysql.server start`
 * `mysql -u root -e 'CREATE DATABASE pontoon CHARACTER SET utf8;'`
 * `./manage.py syncdb --noinput && ./manage.py migrate`
 * `mysql -u root pontoon -e 'ALTER TABLE base_entity CONVERT TO CHARACTER SET utf8 COLLATE utf8_bin;'`
 * `mysql -u root pontoon -e 'ALTER TABLE base_translation CONVERT TO CHARACTER SET utf8 COLLATE utf8_bin;'`
5. Populate database with test project:
 * `./manage.py update_projects`
6. Run development server:
 * `./manage.py runserver`
 * Point your browser to [http://localhost:8000](http://localhost:8000)

For [admin](http://localhost:8000/admin/) access, create admin account with `./manage.py createsuperuser`.

__Mac users__: see workarounds for possible issues with [installing requirements](/../../issues/16) or [syncing database](/../../issues/18).

Local settings
--------------
 * `MICROSOFT_TRANSLATOR_API_KEY`: set [Microsoft Translator API key](http://msdn.microsoft.com/en-us/library/hh454950) to use machine translation.
 * `GOOGLE_ANALYTICS_KEY`: set [Google Analytics key](https://www.google.com/analytics/) to use Google Analytics.
 * `MOZILLIANS_API_KEY`: set [Mozillians API key](https://wiki.mozilla.org/Mozillians/API-Specification) to grant permission to Mozilla localizers.

Updates
-------
To sync your repository with upstream changes, just update the code using git:

* `git pull && git submodule sync --quiet && git submodule update --init --recursive`

Get involved
------------
* File a [bug](https://bugzilla.mozilla.org/enter_bug.cgi?product=Webtools&component=Pontoon&rep_platform=all&op_sys=all)
* Read more on the [Wiki](https://github.com/mathjazz/pontoon/wiki)
* Join #pontoon on [IRC](https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon)

Servers
-------
* [Development](https://pontoon-dev.allizom.org/)
* [Production](https://pontoon.mozilla.org/)

License
-------
This software is licensed under the [New BSD License](http://creativecommons.org/licenses/BSD/). For more information, read the file `LICENSE`.
