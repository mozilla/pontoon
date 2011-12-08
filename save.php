<?php
  /* Save translations in appropriate form */ 
  
  $type = $_POST['type'];
  
  if ($type == 'json') {
    header('Content-disposition: attachment; filename='.$_POST['locale'].'.json');
    header('Content-type: application/json');
    echo stripslashes($_POST['data']);

  } else if ($type == 'html') {
    //

  } else if ($type == 'server') {

  }
  
?>
