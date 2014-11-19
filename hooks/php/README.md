PHP Pontoon Hook
================
This hook enables a PHP website with gettext support to use [Pontoon][1] as a live localization tool.

[1]: https://github.com/mathjazz/pontoon
 
Usage
-----
 1. Add <?php require_once('path/to/pontoon.php'); ?> to your <head> element.
 1. Add <?php Pontoon::header(); ?> to your <head> element.
 1. Find & Replace gettext function calls _('string') with Pontoon function calls _w('string').

License
-------
This software is licensed under the [New BSD License](http://creativecommons.org/licenses/BSD/). For more information, read the file `LICENSE`.
