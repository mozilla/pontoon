<?php
  /* Save translations in appropriate form */ 
  
  $type = $_POST['type'];
  $data = $_POST['data'];
  header('Content-disposition: attachment; filename='.$_POST['locale'].'.'.$type);

  if ($type == 'json') {
    header('Content-type: application/json');
  } else if ($type == 'html') {
    header('Content-type: text/html');
  }

  if (get_magic_quotes_gpc()) { // Deprecated starting in PHP 5.3.0
    echo stripslashes($data);
  } else {
    echo $data;
  }
  
?>
