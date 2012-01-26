<?php
  /* Verify BrowserID assertion */ 

  $params = array('http' => array(
    'method' => 'POST',
    'content' => 'assertion='.$_GET['assertion'].'&audience='.$_GET['audience']
  ));

  $stream = fopen('https://browserid.org/verify', 'r', false, stream_context_create($params));  
  echo stream_get_contents($stream);  
?>