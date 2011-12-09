<?php
  /* Save translations in appropriate form */ 
  
  $type = $_POST['type'];
  header('Content-disposition: attachment; filename='.$_POST['locale'].'.'.$type);

  if ($type == 'json') {
    header('Content-type: application/json');
  } else if ($type == 'html') {
    header('Content-type: text/html');
  }

  echo stripslashes($_POST['data']);
  
?>
