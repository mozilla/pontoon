Hook components
===============

The hook component(s) are the part of the web app that hook into the target project. As of yet, these components are only available in PHP and there are only two pieces to this:

* a `_w()` function that is a wrapper for gettext's `_()`. It marks strings for localization with Pontoon comments that can then be parsed by the client component. You want to use `_w()` everywhere where you used `_()` before. A simple search-and-replace can achieve that.
* `header_tags()` ouputs a (set of) HTML (meta) tags that can be read by the client component and indicate that the current page is capable of being translated with Pontoon. You need to insert a call to `header_tags` to your project's view headers, so that the meta tag is printed out.