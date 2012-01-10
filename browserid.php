<?php
  /* Verify BrowserID assertion */ 
  $url = 'https://browserid.org/verify';
  
  $data = array(
    'assertion' => $_GET['assertion'],
    'audience' => $_GET['audience']
  );
  
  $params = array('http' => array(
                'method' => 'POST',
                'content' => $data,
                'header' => 'Content-Type: application/json'              
  ));
  
  $ctx = stream_context_create($params);
  $fp = @fopen($url, 'rb', false, $ctx);
  
  if (!$fp) {
    throw new Exception("Problem with $url, $php_errormsg");
  }
  
  $response = @stream_get_contents($fp);
  
  if ($response === false) {
    throw new Exception("Problem reading data from $url, $php_errormsg");
  }
  
  echo $response;
?>