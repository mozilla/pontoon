.. _bestpractices:

==============
Best Practices
==============

This page lists several best practices for writing secure web applications
with playdoh.


``|safe`` considered harmful
----------------------------

Using something like ``mystring|safe`` in a template will prevent Jinja2 from
auto-escaping it. Sadly, this requires us to be really sure that ``mystring``
is not raw, user-entered data. Otherwise we introduce an XSS vulnerability.

``|safe`` is safe to use in cases where, for example, you have a localized
string that contains some HTML::

    {{ _('Welcome to <strong>playdoh</strong>!')|safe }}


String interpolation
~~~~~~~~~~~~~~~~~~~~

When you *interpolate* data into such a string, do not use ``|f(...)|safe``.
The data could be unsafe. Instead, use the helper ``|fe(...)``. It will
escape all its arguments before doing string interpolation, then return
HTML that's safe to use::

    {{ _('Welcome back, <strong>{username}</strong>!')|fe(username=user.display_name) }}

``|f(...)|safe`` is to be considered unsafe and should not pass code review.

If you interpolate into a base string that does *not contain HTML*, you may
keep on using ``|f(...)`` without ``|safe``, of course, as it will be
auto-escaped on output::

    {{ _('Author name: {author}')|f(author=user.display_name) }}


Form fields
~~~~~~~~~~~
Jinja2, unlike Django templates, by default does not consider Django forms
"safe" to display. Thus, you'd use something like ``{{ form.myfield|safe }}``.

In order to minimize the use of ``|safe`` (and thus possible unsafe uses of
it), playdoh monkey-patches the Django forms framework so that form fields'
HTML representations are considered safe by Jinja2 as well. Therefore, the
following works as expected::

    {{ form.myfield }}


Mmmmh, Cookies
--------------

Django's default way of setting a cookie is set_cookie_ on the HTTP response.
Unfortunately, both **secure** cookies (i.e., HTTPS-only) and **httponly**
(i.e., cookies not readable by JavaScript, if the browser supports it) are
disabled by default.

To be secure by default, we use commonware's ``cookies`` app. It makes secure
and httponly cookies the default, unless specifically requested otherwise.

To disable either of these patches, set ``COOKIES_SECURE = False`` or
``COOKIES_HTTPONLY = False`` in ``settings.py``.

You can exempt any cookie by passing ``secure=False`` or ``httponly=False`` to
the ``set_cookie`` call, respectively::

    response.set_cookie('hello', value='world', secure=False, httponly=False)

.. _set_cookie: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpResponse.set_cookie
