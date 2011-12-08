<?php
  /* Verify BrowserID assertion */ 

  $url = 'https://browserid.org/verify';
  $params = 'assertion='.$_GET['assertion'].'&audience='.$_GET['audience'];

  $ch = curl_init($url);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
  curl_exec($ch);
  curl_close($ch);

?>
