Pontoon
=======
Pontoon is a live website localization tool. Instead of extracting original strings and then merging translated strings back, Pontoon can turn any website into editable mode using the [contentEditable attribute][contentEditable].

This enables localizers to translate websites in-place with context and spatial limitations right in front of them. A full list of extracted strings is also available, to help with strings that are hard to reach, e.g. error messages and the `<title>` tag.

To enable localization of your site with Pontoon, simply include the script located at `/static/js/project/pontoon.js` to overcome cross frame scripting, and Pontoon will autodetect strings. Or, to make the best out of Pontoon, fully prepare your site with hooks that will mark strings for localization and include all the neccessary tags.

Installation
------------
Pontoon uses [Playdoh][playdoh], which supports running web apps in virtual machines. This is an ideal way to get started developing Pontoon quickly without dealing with dependancies, compiling things and polluting your development system.

1. Install [VirtualBox][virtualbox] by Oracle to run our VM.
2. Install [Vagrant][vagrant] to easily customize and access our VM:
 * `gem install vagrant` (requires [Ruby][ruby] and [gem][gem], but most modern *NIX systems already have them)
3. Clone Pontoon or your [fork][fork]:
 * `git clone --recursive git://github.com/mathjazz/pontoon.git` 
4. Run a virtual development environment from your working copy directory:
 * `cd pontoon`
 * `vagrant up`

If you’re running it for the first time, `vagrant up` will take a few minutes to download base VM image, boot Ubuntu VM, install all the necessary packages and run initialization scripts.

Usage
-----
You can edit files in your working copy directory (`/pontoon`) locally and they will automatically show up under `/home/vagrant/pontoon` in the VM without any weird FTPing.

1. In not running yet, start the VM from your working copy directory:
 * `vagrant up`
2. Enter VM:
 * `vagrant ssh`
3. Run the development web server (in VM):
 * `cd pontoon`
 * `python manage.py runserver 0.0.0.0:8000`
4. Point your web browser to [http://localhost:8000](http://localhost:8000).

Note that you’ll need to explicitly set the host and port for runserver to be accessible from outside the VM. Vagrant setup already forwards port 8000 (the usual Django development port).

Local settings
--------------

Django local settings file should be stored at `/pontoon/settings/local.py`. Copy contents from `/pontoon/settings/local.py-dist`.
 * `SITE_URL`: required for BrowserID, set if different from `http://127.0.0.1:8000`.
 * `SESSION_COOKIE_SECURE = False`: uncomment if running a local development install without HTTPS to disable HTTPS-only cookies.
 * `MICROSOFT_TRANSLATOR_API_KEY`: set to a valid [Microsoft Translator API key][bdc] to use machine translation.

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

`git pull && git submodule sync --quiet && git submodule update --init --recursive`

To only update Playdoh and submodules, do:

`git pull playdoh master && git submodule foreach git pull origin master`

Get involved
------------
* Join #pontoon on [IRC][irc]
* Follow us on [Twitter][twitter]
* Read more on [Wiki][wiki] 

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
[bdc]: http://www.bing.com/developers/createapp.aspx   "Bing Developer Center"
[irc]:  https://cbe001.chat.mibbit.com/?url=irc%3A%2F%2Firc.mozilla.org%2Fpontoon   "Mibbit"
[twitter]:  https://twitter.com/#!/mozillapontoon   "Mozilla Pontoon on Twitter"
[wiki]:  https://wiki.mozilla.org/L10n:Pontoon   "L10n:Pontoon - MozillaWiki"
[BSD]: http://creativecommons.org/licenses/BSD/
