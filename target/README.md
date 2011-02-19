target components
=================

The target component(s) are the part of the web app that hook into the target application. As of yet, these components are only available in PHP and there are only two pieces to this:

* a `_w()` function that is a wrapper for gettext's `_()`. It outputs localized strings wrapped in HTML comments that can then be parsed by the client component.
* `header_tags()` ouputs a (set of) HTML (meta) tags that can be read by the client component and indicate that the current page is capable of being translated with Pontoon.

You want to use `_w()` everywhere where you used `_()` before. A simple search-and-replace can achieve that.

You need to insert a call to `header_tags` to your app's view headers, so that the meta tag is printed out.

setup
-----

mkdir target/php/locale