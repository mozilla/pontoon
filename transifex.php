<?php

  $locale = $_GET['locale'];
  $username = $_GET['transifex']['username'];
  $password = $_GET['transifex']['password'];
  $project = $_GET['transifex']['project'];
  $resource = $_GET['transifex']['resource'];

  if (get_magic_quotes_gpc()) { // Deprecated starting in PHP 5.3.0
    $data = stripslashes($_GET['transifex']['po']);
  } else {
    $data = $_GET['transifex']['po'];
  }

  /* Save PO file to Pontoon server */
  $handle = fopen($locale.".po", 'w');
  fwrite($handle, $data);
  fclose($handle);

  /* Save PO file to Transifex */
  exec("curl -i -L --user ".$username.":".$password." -F file=@".$locale.".po -X PUT https://www.transifex.net/api/2/project/".$project."/resource/".$resource."/translation/".$locale."/;");

 ?>
