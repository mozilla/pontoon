<?php
  /* Save translations in appropriate form */ 

  header('Content-disposition: attachment; filename=pontoon.json');
  header('Content-type: application/json');

  echo stripslashes($_POST['data']);

?>
