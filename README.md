Pontoon
=======

* Frederic Wenzel <fwenzel@mozilla.com>
* Zbigniew Braniecki <gandalf@mozilla.com>
* Austin King <aking@mozilla.com>

This is a proof-of-concept implementation of an in-place website localization tool, as outlined in <http://ozten.com/psto/2009/08/14/a-sketch-of-po-liveedit/>.

Please note that this is a very early alpha version, under development, and unlikely to do much out of the box. If you are interested in the technology, feel free to step by `#webdev` on <irc://irc.mozilla.org>.

Pontoon.jpg contains a schema of the application's components.

Prerequisites
-------------
...

Usage
-----
Hacking on the demo
Map / on a web server to the root of this project.
Point your browser to /client/wwww

Startup the django server
cd server
python manage.py runserver 0.0.0.0:8000

Update hostnames as needed:
  * lib/pontoon.js - 127.0.0.1:8000 - change to server hostname and port
  * target/php/pontoon.php - 8000 - change port number
License
-------
    ***** BEGIN LICENSE BLOCK *****
    Version: MPL 1.1/GPL 2.0/LGPL 2.1

    The contents of this file are subject to the Mozilla Public License Version 
    1.1 (the "License"); you may not use this file except in compliance with 
    the License. You may obtain a copy of the License at 
    http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS IS" basis,
    WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
    for the specific language governing rights and limitations under the
    License.

    The Original Code is Pontoon.

    The Initial Developer of the Original Code is
    Frederic Wenzel <fwenzel at mozilla dot com>.
    Portions created by the Initial Developer are Copyright (C) 2009
    the Initial Developer. All Rights Reserved.

    Contributor(s):

    Alternatively, the contents of this file may be used under the terms of
    either the GNU General Public License Version 2 or later (the "GPL"), or
    the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
    in which case the provisions of the GPL or the LGPL are applicable instead
    of those above. If you wish to allow use of your version of this file only
    under the terms of either the GPL or the LGPL, and not to allow others to
    use your version of this file under the terms of the MPL, indicate your
    decision by deleting the provisions above and replace them with the notice
    and other provisions required by the GPL or the LGPL. If you do not delete
    the provisions above, a recipient may use your version of this file under
    the terms of any one of the MPL, the GPL or the LGPL.

    ***** END LICENSE BLOCK *****

