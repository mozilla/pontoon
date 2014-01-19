Pontoon
=======
Pontoon is a live website localization tool. Instead of extracting original strings and then merging translated strings back, Pontoon can turn any website into editable mode using the [contentEditable attribute][contentEditable].

This enables localizers to translate websites in-place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag.

To enable localization of your site with Pontoon, simply include the script located at `/static/pontoon.js` to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags.

Installation
------------
Pontoon uses [Playdoh][playdoh], which supports running web apps in virtual machines. This is an ideal way to get started developing Pontoon quickly without dealing with dependancies, compiling things and polluting your development system.

1. Install [VirtualBox][virtualbox] by Oracle to run our VM.
2. Install [Vagrant][vagrant] to easily customize and access our VM:
 * `gem install vagrant` (requires [Ruby][ruby] and [gem][gem], but most modern *NIX systems already have them)
3. Clone Pontoon or your [fork][fork]:
 * `git clone --recursive https://github.com/mathjazz/pontoon.git`
4. Run a virtual development environment from your working copy directory:
 * `cd pontoon`
 * `vagrant up`
5. Install dependencies:
 * `vagrant ssh`
 * `sudo apt-get install python-svn mercurial`

If you’re running it for the first time, `vagrant up` will take a few minutes to download base VM image, boot Ubuntu VM, install all the necessary packages and run initialization scripts.

Usage
-----
You can edit files in your working copy directory (`/pontoon`) locally and they will automatically show up under `/home/vagrant/pontoon` in the VM without any weird FTPing.

1. In not running yet, start the VM from your working copy directory:
 * `vagrant up`
2. Enter VM:
 * `vagrant ssh`
 * `cd pontoon`
3. Run the development web server (in VM):
 * `python manage.py syncdb` [only on first use]
 * `python manage.py migrate` [only on first use]
 * `python manage.py createsuperuser` [only on first use]
 * `python manage.py runserver 0.0.0.0:8000`
4. Point your web browser to [http://localhost:8000](http://localhost:8000).

Note that you’ll need to explicitly set the host and port for runserver to be accessible from outside the VM. Vagrant setup already forwards port 8000 (the usual Django development port).

Local settings
--------------

Django local settings file should be stored at `/pontoon/settings/local.py`. Copy contents from `/pontoon/settings/local.py-dist`.
 * `SITE_URL`: required for BrowserID, set if different from `http://127.0.0.1:8000`.
 * `HMAC_KEYS`: set or uncomment if you need bcrypt, e.g. when running `./manage.py createsuperuser`.
 * `SESSION_COOKIE_SECURE = False`: uncomment if running a local development install without HTTPS to disable HTTPS-only cookies.
 * `MICROSOFT_TRANSLATOR_API_KEY`: set to a valid [Microsoft Translator API key][bdc] to use machine translation.
 * `GOOGLE_ANALYTICS_KEY`: set to a valid [Google Analytics key][ga] to use Google Analytics.
 * `MOZILLIANS_API_KEY`: set to a valid [Mozillians API key][mak] to grant permission to Mozilla localizers.

Hooks
--------------

To use PHP hooks:
 * Link `/hooks/` to your web server's document root.
 * Store Pontoon application path in the $path variable in `/hooks/php/local-settings.php` if different from `http://localhost:8000`.

To extract strings, run:
 * `xgettext -L PHP --keyword=_w --from-code=UTF-8 --output=messages.pot *.php`

Updates
-------
To sync your repository with upstream changes, just update the code using git:

* `git pull && git submodule sync --quiet && git submodule update --init --recursive`

To only update Playdoh submodules, do:

* `git submodule foreach git pull origin master`
* `git commit -am "Updating Playdoh submodules"`

Get involved
------------
* File an [issue][issue]
* Read more on the [Wiki][wiki]
* Join #pontoon on [IRC][irc]
* Follow us on [Twitter][twitter]

License
-------
This software is licensed under the [New BSD License][BSD]. For more information, read the file ``LICENSE``.

[contentEditable]:  https://developer.mozilla.org/en/DOM/element.contentEditable   "Element.contentEditable - MDN"
[playdoh]:  https://github.com/mozilla/playdoh   "Playdoh"
[virtualbox]:  https://www.virtualbox.org/wiki/Downloads   "VirtualBox Download"
[vagrant]:  http://vagrantup.com/docs/getting-started/index.html   "Vagrant: Getting Started"
[ruby]:  http://www.ruby-lang.org/   "Ruby"
[gem]:  http://rubygems.org/   "RubyGems.org"
[fork]:  http://help.github.com/fork-a-repo/   "Fork A Repo"
[bdc]: http://msdn.microsoft.com/en-us/library/hh454950   "MSDN"
[ga]: https://www.google.com/analytics/   "Google Analytics"
[mak]: https://wiki.mozilla.org/Mozillians/API-Specification   "Mozillians API Specification"
[irc]:  https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon   "Mibbit"
[issue]:  https://github.com/mathjazz/pontoon/issues   "Pontoon issues"
[wiki]:  https://github.com/mathjazz/pontoon/wiki   "Pontoon wiki"
[twitter]:  https://twitter.com/#!/mozillapontoon   "Pontoon on Twitter"
[BSD]: http://creativecommons.org/licenses/BSD/
