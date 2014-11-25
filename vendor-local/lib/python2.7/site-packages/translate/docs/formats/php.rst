
.. _php:

PHP
***

Many :wp:`PHP` programs make use of a localisable string array.  The toolkit
supports the full localisation of such files with :doc:`/commands/php2po` and
po2php.


.. _php#conformance:

Conformance
===========

Our format support allows:

* `Single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings (both for keys and values)

  .. code-block:: php

      <?php
      $variable = 'string';
      $messages["language"] = 'Language';
      define('item', "another string");


* PHP simple variable syntax

  .. code-block:: php

      <?php
      $variable = 'string';
      $another_variable = "another string";


* PHP square bracket array syntax

  .. code-block:: php

      <?php
      $messages['language'] = 'Language';
      $messages['file'] = "File";
      $messages["window"] = 'Window';
      $messages["firewall"] = "Firewall";


* PHP array syntax

  .. versionadded:: 1.7.0

  .. code-block:: php

      <?php
      // Can be 'array', 'Array' or 'ARRAY'.
      $lang = array(
         'name' => 'value',
         'name2' => "value2",
         "key1" => 'value3',
         "key2" => "value4",
      );


* PHP define syntax

  .. versionadded:: 1.10.0

  .. code-block:: php

      <?php
      define('item', 'string');
      define('another_item', "another string");
      define("key", 'and another string');
      define("another_key", "yet another string");


* Escape sequences (both for `single
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
  and `double
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
  quoted strings)

  .. code-block:: php

      <?php
      $variable = 'He said: "I\'ll be back"';
      $another_variable = "First line \n second line";
      $key = "\tIndented string";


* Multiline entries

  .. code-block:: php

      <?php
      $lang = array(
         'name' => 'value',
         'info' => 'Some hosts disable automated mail sending
	        on their servers. In this case the following features
	        cannot be implemented.',
         'name2' => 'value2',
      );


* Various layouts of the id

  .. code-block:: php

      <?php
      $string['name'] = 'string';
      $string[name] = 'string';
      $string[ 'name' ] = 'string';


* Comments

  .. versionchanged:: 1.10.0

  .. code-block:: php

      <?php
      # Hash one-line comment
      $messages['language'] = 'Language';

      // Double slash one-line comment
      $messages['file'] = 'File';

      /*
         Multi-line
         comment
      */
      $messages['help'] = 'Help';


* Whitespace before end delimiter

  .. versionadded:: 1.10.0

  .. code-block:: php

      <?php
      $variable = 'string'     ;

      $string['name'] = 'string'     ;

      $lang = array(
         'name' => 'value'           ,
      );

      define('item', 'string'    );


* Nested arrays with any number of nesting levels

  .. versionadded:: 1.11.0

  .. code-block:: php

      <?php
      $lang = array(
         'name' => 'value',
         'datetime' => array(
            'TODAY' => 'Today',
            'YESTERDAY'	=> 'Yesterday',
            'AGO' => array(
                0 => 'less than a minute ago',
                2 => '%d minutes ago',
                60 => '1 hour ago',
            ),
            'Converted' => 'Converted',
            'LAST' => 'last',
         ),
      );

* Whitespace in the array declaration

  .. versionadded:: 1.11.0

  .. code-block:: php

      <?php
      $variable = array    (
         "one" => "this",
         "two" => "that",
      );

* Blank array declaration, then square bracket syntax to fill that array

  .. versionadded:: 1.12.0

  .. code-block:: php

      <?php
      global $messages;
      $messages = array();

      $messages['language'] = 'Language';
      $messages['file'] = 'File';


.. _php#non-conformance:

Non-Conformance
===============

The following are not yet supported:

* Keyless arrays:

  .. code-block:: php

      <?php
      $days = array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');

      $messages['days_short'] = array('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');


* Nested arrays without key for a nested array:

  .. code-block:: php

      <?php
      $lang = array(array("key" => "value"));


* Array entries without ending comma:

  .. code-block:: php

      <?php
      $variable = array(
         "one" => "this",
         "two" => "that"
      );


* String concatenation:

  .. code-block:: php

      <?php
      $messages['welcome'] = 'Welcome ' . $name . '!';
      $messages['greeting'] = 'Hi ' . $name;


* Assignment in the same line a multiline comment ends:

  .. code-block:: php

      <?php
      /*
         Multi-line
         comment
      */ $messages['help'] = 'Help';


* `Heredoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc>`_
* `Nowdoc
  <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.nowdoc>`_

